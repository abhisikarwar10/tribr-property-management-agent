# Generation module — wraps LLM call with context injection
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def get_llm():
    return OllamaLLM(model="llama3.2", temperature=0)

PROMPT_TEMPLATE = """
You are an expert Indian real estate lawyer analyzing a Builder Buyer Agreement.
Use ONLY the context below to answer the question.
If the answer is not in the context, say "This information is not found in the document."

Context:
{context}

Question: {question}

Answer clearly and cite which clause or section supports your answer:
"""

def generate_answer(query: str, retrieved_chunks: list) -> str:
    context_parts = []
    for doc,score in retrieved_chunks:
        # if isinstance(item, tuple):
        #     doc, score = item
        # else:
        #     doc = item
        page = doc.metadata.get('page', 'unknown')
        context_parts.append(f"[Page {page}]\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    llm = get_llm()
    chain = prompt | llm

    answer = chain.invoke({"context": context, "question": query})
    return answer
