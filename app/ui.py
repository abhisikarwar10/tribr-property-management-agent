import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Property Management AI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Property Management AI Agent")
st.caption("Powered by LangGraph + Groq + RAG")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Sidebar
with st.sidebar:
    st.header("Quick Actions")
    
    quick_queries = [
        "Which tenants have overdue payments?",
        "Check who is overdue and draft a reminder for them",
        "What is the late payment penalty according to the lease?",
        "What is the notice period for terminating the lease?",
        "What is the security deposit amount?",
        "What are the maintenance responsibilities of the tenant?",
    ]
    
    for q in quick_queries:
        if st.button(q, use_container_width=True):
            st.session_state.pending_query = q
    
    st.divider()
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()
    
    st.divider()
    st.markdown("**Agent Tools**")
    st.markdown("✅ Payment tracker")
    st.markdown("✅ Notice drafter")
    st.markdown("✅ Lease document RAG")
    st.markdown("✅ Multi-step reasoning")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle quick action
if "pending_query" in st.session_state:
    query = st.session_state.pop("pending_query")
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.write(query)
    
    with st.chat_message("assistant"):
        with st.spinner("Agent thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": query,
                        "session_id": st.session_state.session_id
                    }
                )
                data = response.json()
                st.session_state.session_id = data["session_id"]
                answer = data["answer"]
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.rerun()

# Chat input
if query := st.chat_input("Ask anything about your properties..."):
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.write(query)
    
    with st.chat_message("assistant"):
        with st.spinner("Agent thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": query,
                        "session_id": st.session_state.session_id
                    }
                )
                data = response.json()
                st.session_state.session_id = data["session_id"]
                answer = data["answer"]
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.rerun()