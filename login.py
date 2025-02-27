import streamlit as st
from supabase import create_client, Client
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit UI for authentication
st.title("AI Persona Chat - Login")

# User authentication selection
choice = st.radio("Select an option:", ["Login", "Sign Up"])

if choice == "Sign Up":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        response = supabase.auth.sign_up({"email": email, "password": password})
        if "error" in response:
            st.error("Sign up failed")
        else:
            st.success("Account created successfully! Please log in.")

elif choice == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if "error" in response:
            st.error("Login failed")
        else:
            st.session_state["user"] = response.user
            st.success("Login successful!")
            st.write("Welcome, ", email)
            st.switch_page("pages/personas.py")

