# Property Management AI Agent

A production-grade AI agent for property management built with LangGraph, Groq, and RAG.

## What it does

Natural language interface for property managers:
- Check which tenants have overdue payments
- Draft professional payment reminders automatically
- Query lease agreement for any clause or term
- Multi-step reasoning — "check who is overdue and draft reminders for all of them"

## Architecture
User Query
↓
[LangGraph Router] — keyword fast-path or LLM agent
↓                           ↓
[Direct Answer]         [LLM Agent — Llama 3.3 70B on Groq]
↓
decides tool sequence autonomously
↓
┌─────────────────┼─────────────────┐
↓                 ↓                 ↓
[Payment Tracker]   [Notice Drafter]   [Lease RAG]
SQLAlchemy/SQLite   Groq LLM           ChromaDB +
generation         Hybrid Search

## Stack
- LangGraph — agent orchestration
- Groq (Llama 3.3 70B) — LLM inference
- LangSmith — observability and tracing
- ChromaDB + BM25 — hybrid RAG retrieval
- SQLAlchemy — payment database
- FastAPI — REST API
- Streamlit — UI

## RAGAS Evaluation (RAG component)
| Metric | Score |
|---|---|
| Faithfulness | 1.0 |
| Context Recall | 1.0 |
| Context Precision | 1.0 |

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/property-management-agent
cd property-management-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Add your keys to .env
cp .env.example .env

# Start API
python3 main.py

# Start UI (new terminal)
streamlit run app/ui.py
```

## API

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | Service health check |
| /query | POST | Natural language agent query |

## Environment Variables
GROQ_API_KEY=your-groq-key
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=property-management-agent
