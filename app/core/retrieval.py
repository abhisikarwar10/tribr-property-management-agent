from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os

CHROMA_PATH = "data/processed/chroma_db"

def get_embeddings():
    """Load local embedding model via Ollama"""
    return OllamaEmbeddings(model="nomic-embed-text")

def create_vectorstore(chunks):
    """Embed chunks and store in ChromaDB"""
    print("Embedding chunks... this may take a minute")
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Vectorstore created and persisted at {CHROMA_PATH}")
    return vectorstore

def load_vectorstore():
    """Load existing vectorstore from disk"""
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    return vectorstore

def retrievechunks(query:str,vectorstore,k:int=4):
    """return top k most relevant chunks for a given query"""
    results = vectorstore.similarity_search_with_score(query, k=k*2)
    seen = set()
    unique_results = []

    for doc, score in results:
        content = doc.page_content.strip()
        if content not in seen:
            seen.add(content)
            unique_results.append((doc, score))
        if len(unique_results) == k:
            break

    for i, (doc, score) in enumerate(results):
        print(f"\n[Chunk {i+1}] Score: {score:.4f} | Page: {doc.metadata['page']}")
        print(doc.page_content[:200])  # Print first 200 chars of chunk
    return unique_results