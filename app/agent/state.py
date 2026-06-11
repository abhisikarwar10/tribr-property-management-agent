from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    property_id: str
    tenant_name: str
    route: Optional[str]