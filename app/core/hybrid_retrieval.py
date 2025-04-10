from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from rank_bm25 import BM25Okapi
import numpy as np

CHROMA_PATH = "data/processed/chroma_db"

def get_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")

def load_vectorstore():
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def build_bm25_index(chunks):
    # BM25 index is rebuilt per query — consider caching for performance
    """Build BM25 index from chunks"""
    tokenized = [chunk.page_content.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized)
    return bm25

def hybrid_retrieve(query: str, vectorstore, all_chunks: list, k: int = 4):
    # k=4 chosen empirically — increase for longer docs
    """
    Combine semantic search + BM25 keyword search
    using Reciprocal Rank Fusion (RRF)
    """
    # --- Semantic search ---
    semantic_results = vectorstore.similarity_search_with_score(query, k=k*2)

    # --- BM25 keyword search ---
    bm25 = build_bm25_index(all_chunks)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    top_bm25_indices = np.argsort(bm25_scores)[::-1][:k*2]

    # --- Reciprocal Rank Fusion ---
    rrf_scores = {}

    # Score semantic results
    for rank, (doc, score) in enumerate(semantic_results):
        doc_id = doc.page_content[:50]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(rank + 60)

    # Score BM25 results
    for rank, idx in enumerate(top_bm25_indices):
        doc_id = all_chunks[idx].page_content[:50]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(rank + 60)

    # Build final ranked list
    all_docs = {doc.page_content[:50]: doc for doc, _ in semantic_results}
    for idx in top_bm25_indices:
        doc_id = all_chunks[idx].page_content[:50]
        all_docs[doc_id] = all_chunks[idx]

    # Sort by RRF score
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    # Deduplicate and return top k
    seen = set()
    results = []
    for doc_id, rrf_score in ranked:
        if doc_id not in seen and doc_id in all_docs:
            seen.add(doc_id)
            results.append((all_docs[doc_id], rrf_score))
        if len(results) == k:
            break

    # for i, (doc, score) in enumerate(results):
    #     print(f"\n[Chunk {i+1}] RRF Score: {score:.4f} | Page: {doc.metadata['page']}")
    #     print(doc.page_content[:300])

    return results
    
def hybrid_retrieve_with_transform(query: str, vectorstore, all_chunks: list, k: int = 4):
    from app.core.query_transform import transform_query
    
    queries = transform_query(query)
    
    # Count appearances + accumulate scores
    doc_scores = {}
    doc_objects = {}
    
    for q in queries:
        results = hybrid_retrieve(q, vectorstore, all_chunks, k=k)
        for doc, score in results:
            doc_id = doc.page_content[:50]
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_objects[doc_id] = doc
            doc_scores[doc_id] += score  # accumulate across queries
    
    # Sort by accumulated score
    ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    
    results = [(doc_objects[doc_id], score) for doc_id, score in ranked]
    
    # print(f"\n--- Final Merged Results ({len(results)} chunks) ---")
    # for i, (doc, score) in enumerate(results):
    #     print(f"[Chunk {i+1}] Accumulated Score: {score:.4f} | Page: {doc.metadata['page']}")
    #     print(doc.page_content[:200])
    
    return results