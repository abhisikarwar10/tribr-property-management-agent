from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from app.agent.graph import agent
import uuid

app = FastAPI(
    title="Property Management AI Agent",
    description="AI-powered property management — payments, lease queries, notices",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    property_id: Optional[str] = ""
    tenant_name: Optional[str] = ""

class QueryResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    success: bool

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "property-management-agent"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = agent.invoke({
            "messages": [HumanMessage(content=request.query)],
            "property_id": request.property_id,
            "tenant_name": request.tenant_name
        })
        
        answer = result["messages"][-1].content
        
        return QueryResponse(
            session_id=session_id,
            query=request.query,
            answer=answer,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))