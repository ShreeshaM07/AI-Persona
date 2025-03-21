import streamlit as st
from supabase import create_client, Client
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check if user is logged in
if "user" not in st.session_state:
    st.error("Please log in first!")
    st.stop()

st.title("Create or Select Your AI Persona")

# Retrieve current user's ID
user_id = st.session_state["user"].get("id") if isinstance(st.session_state["user"], dict) else st.session_state["user"].id
# st.write(st.session_state["user"])

# Fetch existing personas
personas = supabase.table("personas").select("*").eq("user_id", user_id).execute()
# st.write(personas)

persona_data = {p["name"]: p for p in personas.data} if personas.data else {}
persona_list = ["Create New"] + list(persona_data.keys())

if st.button("Evaluate Candidate"):
    st.switch_page("pages/evaluate.py")

# Option to select an existing persona
selected_persona = st.selectbox("Choose an existing persona:", persona_list)

if selected_persona == "Create New":
    st.subheader("Create a New Persona")
    name = st.text_input("Persona Name")
    personality_trait = st.text_input("Personality traits")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Other"])
    location = st.text_input("Location")
    occupation = st.text_input("Occupation")
    education = st.text_input("Education")
    communication_style = st.selectbox("Communication Style", ["Formal", "Casual", "Technical", "Humorous"])
    history = st.text_input("Back history")

    if st.button("Save Persona"):
        data = {
            "user_id": user_id,
            "traits": personality_trait,
            "age": age,
            "gender": gender,
            "location": location,
            "occupation": occupation,
            "name": name,
            "history": history,
            "education": education,
            "communication_style": communication_style,
        }
        try:
            response = supabase.table("personas").insert(data).execute()
            st.success("Persona Created!")
            st.session_state["selected_persona"] = data  # Store new persona in session
            time.sleep(1)
            st.rerun()  # Refresh the page to show the new persona   
        except Exception as e:
            print(e)
            st.error("Error creating persona.")


else:
    st.success(f"Selected Persona: {selected_persona}")
    st.session_state["selected_persona"] = persona_data[selected_persona]  # Store selected persona
    st.switch_page("pages/chat.py")  # Redirect to chat page
