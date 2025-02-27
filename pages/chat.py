import streamlit as st
import asyncio
from pages.llm import get_ai_response
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://mpfpnpulbnxajowozgoc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1wZnBucHVsYm54YWpvd296Z29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAwNTQ0MTcsImV4cCI6MjA1NTYzMDQxN30.Cp-9Ct-k_H-IXw5YWB_sq0l5eqFAxsxgYsw-nYYXtGU"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("AI Persona Chat")

# Check if a persona is selected
if "selected_persona" not in st.session_state:
    st.error("Please select a persona first!")
    st.stop()

# Retrieve user ID
user_id = st.session_state["user"].get("id") if isinstance(st.session_state["user"], dict) else st.session_state["user"].id

# Retrieve persona details from session state
select_persona_background = st.session_state["selected_persona"]
st.write(select_persona_background)

# Fetch the selected persona's ID from the database
persona_name = st.session_state["selected_persona"]["name"]
persona_query = supabase.table("personas").select("id").eq("user_id", user_id).eq("name", persona_name).execute()

st.write(persona_query)

if not persona_query.data:
    st.error("Persona not found!")
    st.stop()

persona_id = persona_query.data[0]["id"]  # Get the persona     ID
st.write(persona_id)
# Fetch previous chat history for this persona
chat_query = supabase.table("chat_history").select("role, content").eq("persona_id", persona_id).order("timestamp").execute()
st.session_state.chat_history = chat_query.data if chat_query.data else []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to chat history
    user_message = {"role": "user", "content": user_input}
    st.session_state.chat_history.append(user_message)

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response using LLM
    ai_response = asyncio.run(get_ai_response(select_persona_background, st.session_state.chat_history, user_input))
    ai_message = {"role": "assistant", "content": ai_response}

    # Add AI response to chat history
    st.session_state.chat_history.append(ai_message)

    # Save both messages to Supabase
    supabase.table("chat_history").insert([
        {"persona_id": persona_id, "role": "user", "content": user_input},
        {"persona_id": persona_id, "role": "assistant", "content": ai_response}
    ]).execute()

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response)
