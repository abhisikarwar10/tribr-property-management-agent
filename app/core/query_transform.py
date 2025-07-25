from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def get_llm():
    return OllamaLLM(model="llama3.2", temperature=0)

TRANSFORM_PROMPT = """
You are an expert at searching Indian real estate legal documents.

Convert the question below into 3 different plain text search phrases.
Use formal legal terminology found in Builder Buyer Agreements.
Do NOT use boolean operators, quotes, or brackets.
Write each query as a simple phrase, like it would appear in the document.

Original question: {question}

Return ONLY 3 plain phrases, one per line, no numbering, no explanation:
"""

def transform_query(question: str) -> list[str]:
    """Transform user question into multiple legal search queries"""
    llm = get_llm()
    prompt = PromptTemplate(
        template=TRANSFORM_PROMPT,
        input_variables=["question"]
    )
    chain = prompt | llm
    result = chain.invoke({"question": question})
    
    # Parse the 3 queries
    queries = [q.strip() for q in result.strip().split("\n") if q.strip()]
    queries = queries[:3]  # ensure max 3
    # 3 queries balances recall vs latency
    
    # Always include original question too
    queries.append(question)
    
    print(f"\n--- Query Transformation ---")
    print(f"Original: {question}")
    for i, q in enumerate(queries):
        print(f"Query {i+1}: {q}")
    
    return queries