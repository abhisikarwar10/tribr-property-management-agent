import os

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from app.agent.state import AgentState
from app.tools.payment_tool import get_payment_status, get_overdue_tenants
from app.tools.draft_tool import draft_payment_notice
from app.tools.rag_tool import query_lease_document
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import re

# --- System prompt ---
# SYSTEM_PROMPT = """You are a helpful property management assistant.
# You have access to tools to check payments, draft notices, and query lease documents.

# IMPORTANT RULES:
# 1. When a tool returns results, quote the key facts EXACTLY — especially amounts, dates, and clause numbers
# 2. Never paraphrase specific numbers or legal clauses — use the exact figures from tool results
# 3. Never ask for clarification if you can use a tool to find the answer
# 4. Always mention which section or clause supports your answer
# 5. Always use the send_payment_notice tool to draft payment reminders or notice — never write them yourself"""

# # --- Define tools ---
# @tool
# def check_payment_status(tenant_name: str) -> str:
#     """Check payment history for a specific tenant by name"""
#     return get_payment_status(tenant_name)

# @tool
# def check_overdue_tenants() -> str:
#     """Get list of all tenants with pending or overdue payments"""
#     return get_overdue_tenants()

# @tool
# def send_payment_notice(tenant_name: str, property_id: str, amount: float, days_overdue: int) -> str:
#     """Use this to draft a payment reminder or notice message for a tenant who has overdue rent. 
#     Always use this tool when asked to draft, write, or send a payment reminder."""
#     return draft_payment_notice(tenant_name, property_id, amount, days_overdue)

# @tool
# def query_lease(question: str) -> str:
#     """Query the lease agreement document to answer questions about terms, penalties, clauses"""
#     return query_lease_document(question)

# # --- Tools list ---
# tools = [check_payment_status, check_overdue_tenants, send_payment_notice, query_lease]

# # --- LLM ---
# llm = ChatOllama(model="llama3.1:8b", temperature=0)
# llm_with_tools = llm.bind_tools(tools)

# # --- Agent node ---
# def agent_node(state: AgentState) -> AgentState:
#     messages = state["messages"]
#     if not any(isinstance(m, SystemMessage) for m in messages):
#         messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
#     response = llm_with_tools.invoke(messages)
#     return {"messages": [response]}

# # --- Routing ---
# def should_continue(state: AgentState) -> str:
#     last_message = state["messages"][-1]
#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "use_tool"
#     return "end"

# # --- Build graph ---
# def build_graph():
#     graph = StateGraph(AgentState)
#     graph.add_node("agent", agent_node)
#     graph.add_node("tools", ToolNode(tools))
#     graph.set_entry_point("agent")
#     graph.add_conditional_edges(
#         "agent",
#         should_continue,
#         {"use_tool": "tools", "end": END}
#     )
#     graph.add_edge("tools", "agent")
#     return graph.compile()

# agent = build_graph()

#****llm deciding which tools to use based on user query and tool results
#---------------------------------------------#

#****hybrid --> explicit routing and llm deciding only for multi step queries

# --- System prompt ---
SYSTEM_PROMPT = """You are a helpful property management assistant.
You manage rental properties, tenant payments, lease agreements, and maintenance requests.

TOOL SELECTION GUIDE — follow this exactly:
- "who hasn't paid" / "overdue" / "pending payments" / "which tenants" → use check_overdue_tenants_tool
- "payment history for [name]" / "check payment for [name]" → use check_payment_status_tool
- "draft reminder" / "send notice" / "payment reminder for [name]" → use send_payment_notice_tool
- "what does the lease say" / "clause" / "lease penalty" / "agreement terms" → use query_lease_tool

RULES:
1. Always use tools — never answer from your own knowledge
2. Call each tool ONLY ONCE per query — if you already have a tool result, use it to answer immediately
3. After receiving a tool result, you MUST provide a final text answer — do NOT call the same tool again
4. Quote exact amounts, dates, clause numbers from tool results
5. Never fabricate clause numbers or legal text
6. query_lease_tool is ONLY for reading the lease PDF — never use it for tenant payment data"""

# --- Tools ---
@tool
def check_overdue_tenants_tool() -> str:
    """Get the list of tenants who have NOT paid rent this month from the payment database"""
    print("[Tool Called] check_overdue_tenants_tool")
    result = get_overdue_tenants()
    print(f"[Tool Result] {result}")
    return result

@tool
def check_payment_status_tool(tenant_name: str) -> str:
    """Check payment history for a specific tenant by name from the payment database"""
    print(f"[Tool Called] check_payment_status_tool | tenant: {tenant_name}")
    result = get_payment_status(tenant_name)
    print(f"[Tool Result] {result}")
    return result

@tool
def send_payment_notice_tool(tenant_name: str, property_id: str, amount: str, days_overdue: str) -> str:
    """Draft a payment reminder notice for a tenant with overdue rent. Use ONLY when explicitly asked to draft or send a reminder."""
    print(f"[Tool Called] send_payment_notice_tool | tenant: {tenant_name} | property: {property_id} | amount: {amount} | days: {days_overdue}")
    result = draft_payment_notice(tenant_name, property_id, float(amount), int(days_overdue))
    print(f"[Tool Result] {result[:100]}...")
    return result

@tool
def query_lease_tool(question: str) -> str:
    """Query the lease agreement PDF document ONLY for legal terms, clauses, and conditions written in the lease. Do NOT use this for tenant payment data."""
    print(f"[Tool Called] query_lease_tool | question: {question}")
    result = query_lease_document(question)
    print(f"[Tool Result] {result[:100]}...")
    return result

tools = [check_overdue_tenants_tool, check_payment_status_tool, send_payment_notice_tool, query_lease_tool]

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# --- Fast router for high-frequency known intents ---
def fast_route(query: str) -> str:
    # q = query.lower()
    
    # if any(w in q for w in ["overdue", "pending", "unpaid", "which tenant",
    #                           "who hasn't paid", "haven't paid", "not paid",
    #                           "who owes", "outstanding payment", "due payment"]):
    #     return "overdue"
    
    # if re.match(r"^check payment(s)? (for|of) .+", q):
    #     return "payment_status"
    
    return "llm"

# --- Router node ---
def router_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1].content
    route = fast_route(last_message)
    print(f"\n[Router] Query: '{last_message[:60]}...' → {route}" if len(last_message) > 60 else f"\n[Router] Query: '{last_message}' → {route}")

    if route == "overdue":
        print("[Router] Fast routing to overdue check — skipping LLM")
        result = get_overdue_tenants()
        print(f"[Router Result] {result}")
        return {"messages": [AIMessage(content=result)]}

    elif route == "payment_status":
        words = last_message.split()
        names = [w for w in words if w[0].isupper() and len(w) > 2]
        tenant_name = " ".join(names[:2]) if len(names) >= 2 else names[0] if names else "unknown"
        print(f"[Router] Fast routing to payment status for: {tenant_name}")
        result = get_payment_status(tenant_name)
        print(f"[Router Result] {result}")
        return {"messages": [AIMessage(content=result)]}

    print("[Router] No fast route matched — sending to LLM agent")
    return {"messages": state["messages"]}

# --- LLM agent node ---
def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    print(f"\n[Agent] Invoking LLM with {len(messages)} messages")
    response = llm_with_tools.invoke(messages)
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"[Agent] LLM wants to call: {[tc['name'] for tc in response.tool_calls]}")
    else:
        print(f"[Agent] LLM returning final answer")
    
    return {"messages": [response]}

# --- Routing decisions ---
def after_router(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and not (hasattr(last, "tool_calls") and last.tool_calls):
        print("[after_router] Fast route answered → END")
        return "end"
    print("[after_router] Needs LLM → agent")
    return "llm"

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        # Check if this exact tool was already called with same args
        tool_name = last.tool_calls[0]["name"]
        tool_args = last.tool_calls[0].get("args", {})
        
        # Look through message history for duplicate tool calls
        for msg in state["messages"][:-1]:
            if (hasattr(msg, "tool_calls") and msg.tool_calls and 
                msg.tool_calls[0]["name"] == tool_name and
                msg.tool_calls[0].get("args", {}) == tool_args):
                print(f"[should_continue] Duplicate tool call detected for {tool_name} — forcing END")
                return "end"
        
        print(f"[should_continue] Tool calls found → use_tool")
        return "use_tool"
    print("[should_continue] No tool calls → END")
    return "end"

# --- Build graph ---
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        after_router,
        {"end": END, "llm": "agent"}
    )

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"use_tool": "tools", "end": END}
    )

    graph.add_edge("tools", "agent")

    return graph.compile()

agent = build_graph()
