from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from datasets import Dataset

def get_ragas_llm():
    return LangchainLLMWrapper(OllamaLLM(model="llama3.2", temperature=0))

def get_ragas_embeddings():
    return LangchainEmbeddingsWrapper(OllamaEmbeddings(model="nomic-embed-text"))

def evaluate_rag(test_cases: list) -> dict:
    """
    test_cases: list of dicts with keys:
        - question
        - answer
        - contexts (list of strings)
        - ground_truth
    """
    dataset = Dataset.from_list(test_cases)

    ragas_llm = get_ragas_llm()
    ragas_embeddings = get_ragas_embeddings()

    metrics = [faithfulness, answer_relevancy, context_precision, context_recall] 

    for metric in metrics:
        metric.llm = ragas_llm
        if hasattr(metric, 'embeddings'):
            metric.embeddings = ragas_embeddings

    results = evaluate(
        dataset=dataset,
        metrics=metrics
    )
    return results





