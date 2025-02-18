from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def get_llm():
    # temperature=0.3 for slightly creative but consistent output
    return OllamaLLM(model="llama3.2", temperature=0.5)

NOTICE_PROMPT = """
You are a property manager drafting a professional but firm payment reminder.

Tenant Name: {tenant_name}
Property: {property_id}
Amount Due: Rs. {amount}
Days Overdue: {days_overdue}
Landlord Name: {landlord_name}

Draft a short, professional payment reminder message (WhatsApp style, under 100 words).
Be polite but firm. Mention the amount and days overdue. End with contact details placeholder.
"""

WELCOME_PROMPT = """
You are a property manager drafting a welcome message for a new tenant.

Tenant Name: {tenant_name}
Property: {property_id}
Move-in Date: {move_in_date}
Monthly Rent: Rs. {amount}
Landlord Name: {landlord_name}

Draft a warm, professional welcome message (under 100 words).
Include rent due date reminder and emergency contact placeholder.
"""

def draft_payment_notice(
    print(f"[DraftTool] Drafting notice for {tenant_name}")
    tenant_name: str,
    property_id: str,
    amount: float,
    days_overdue: int,
    landlord_name: str = "The Management"
) -> str:
    llm = get_llm()
    prompt = PromptTemplate(
        template=NOTICE_PROMPT,
        input_variables=["tenant_name", "property_id", "amount", "days_overdue", "landlord_name"]
    )
    chain = prompt | llm
    return chain.invoke({
        "tenant_name": tenant_name,
        "property_id": property_id,
        "amount": amount,
        "days_overdue": days_overdue,
        "landlord_name": landlord_name
    })

def draft_welcome_message(
    tenant_name: str,
    property_id: str,
    move_in_date: str,
    amount: float,
    landlord_name: str = "The Management"
) -> str:
    llm = get_llm()
    prompt = PromptTemplate(
        template=WELCOME_PROMPT,
        input_variables=["tenant_name", "property_id", "move_in_date", "amount", "landlord_name"]
    )
    chain = prompt | llm
    return chain.invoke({
        "tenant_name": tenant_name,
        "property_id": property_id,
        "move_in_date": move_in_date,
        "amount": amount,
        "landlord_name": landlord_name
    })