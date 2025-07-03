import os
import sys

from app.core.retrieval import load_vectorstore
from app.core.hybrid_retrieval import hybrid_retrieve_with_transform
from app.core.generation import generate_answer
from app.core.ingestion import load_documents, chunk_documents

CHROMA_PATH = "data/processed/chroma_db"
RAW_DATA_PATH = "data/raw"

def query_lease_document(question: str) -> str:
    # TODO: add retry logic for vectorstore timeout
    """Query the tenant's lease agreement using RAG"""
    if not os.path.exists(CHROMA_PATH):
        return "No lease document found. Please upload a document first."

    pdfs = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".pdf")]
    if not pdfs:
        return "No lease document found."

    pdf_path = os.path.join(RAW_DATA_PATH, pdfs[0])
    docs = load_documents(pdf_path)
    chunks = chunk_documents(docs)

    vectorstore = load_vectorstore()
    results = hybrid_retrieve_with_transform(question, vectorstore, chunks)
    answer = generate_answer(question, results)

    return answer