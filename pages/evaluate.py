import asyncio
import streamlit as st
from groq import AsyncGroq
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

async def eval_persona_prompt_alignment(persona_details, chat_responses):
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    messages = [
        {"role": "system", "content": "Evaluate if the AI responses align with the given persona details."},
        {"role": "user", "content": f"Persona details:\n{persona_details}"},
    ]

    for response in chat_responses:
        messages.append({"role": "assistant", "content": response})

    messages.append({"role": "user", "content": "Analyze the above responses and provide an alignment score (0-100) with reasoning."})

    response = await client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=512
    )

    evaluation_result = response.choices[0].message.content
    st.subheader("🔍 Persona Evaluation Result")
    st.write(evaluation_result)

async def eval_candidate_skills(persona_details, chat_history):
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    evaluation_prompt = (
        f"The following conversation is between an AI persona and a candidate. "
        f"The AI persona is role-playing as {persona_details['name']}, who is a {persona_details['occupation']} "
        f"with background in {persona_details['history']}. The candidate is being evaluated based on their responses.\n\n"
        f"### Evaluation Criteria:\n"
        f"1️. **Depth of Knowledge** - Does the candidate show strong understanding and expertise in the concepts?\n"
        f"2️. **Clarity & Communication** - Are their responses well-structured and clear?\n"
        f"3️. **Logical Reasoning** - Do they apply logical thinking to their answers?\n"
        f"4️. **Problem-Solving Ability** - How well do they tackle challenges or tricky questions?\n"
        f"5️. **Confidence & Engagement** - Are they actively engaging or hesitant in responses?\n\n"
        f"Provide a **detailed evaluation** and a **final score (0-100)** based on these factors."
    )

    messages = [{"role": "system", "content": evaluation_prompt}]

    for entry in chat_history:
        role = entry["role"]
        content = entry["content"]
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": "Analyze the above conversation and provide a structured skill evaluation with a score (0-100)."})

    response = await client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=512
    )

    evaluation_result = response.choices[0].message.content
    st.subheader("📊 Candidate Skills Evaluation")
    st.write(evaluation_result)

    return evaluation_result

async def eval_conversation_success(persona_details, chat_history, candidate_evaluation_result):
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    success_criteria_prompt = (
        "Evaluate the AI conversation and user responses based on the following success criteria:\n\n"
        "1. **Context and Scenario-based conversation** - Did the AI follow the intended scenario and maintain coherence?\n"
        "2. **Conversation Accuracy (Target: 75%)** - Did the AI provide factually correct and contextually relevant responses?\n"
        "3. **User Evaluation Accuracy (Target: 80%)** - Based on the AI's evaluation of the user, how accurate and insightful was the assessment?\n\n"
        "You are provided with:\n"
        "- The full conversation history between the AI and the user.\n"
        "- The AI's evaluation of the user.\n\n"
        "Provide a detailed breakdown of each success criterion with individual scores (0-100) and a final aggregated success score."
    )

    messages = [{"role": "system", "content": success_criteria_prompt}]

    for entry in chat_history:
        role = entry["role"]
        content = entry["content"]
        messages.append({"role": role, "content": content})

    messages.append({"role": "assistant", "content": f"AI's User Evaluation: {candidate_evaluation_result}"})
    messages.append({"role": "user", "content": "Analyze the provided data and give a structured evaluation based on the success criteria."})

    response = await client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=512
    )

    evaluation_result = response.choices[0].message.content
    st.subheader("🔎 **Conversation Success Evaluation**")
    st.write(evaluation_result)

def get_personas():
    """Fetch all personas from the database."""
    persona_query = supabase.table("personas").select("id, name").execute()
    return persona_query.data if persona_query.data else []

def get_chat_history(persona_id):
    """Fetch chat history for the selected persona."""
    chat_query = supabase.table("chat_history").select("role, content").eq("persona_id", persona_id).order("timestamp").execute()
    return chat_query.data if chat_query.data else []

# Streamlit UI
st.title("AI Persona Evaluation Dashboard")

# Fetch and display personas
personas = get_personas()
if not personas:
    st.error("No personas found in the database.")
    st.stop()

persona_names = [persona["name"] for persona in personas]
selected_index = st.selectbox("Select a Persona", range(len(persona_names)), format_func=lambda i: persona_names[i])

selected_persona = personas[selected_index]
persona_id = selected_persona["id"]
st.write(f"🔹 **Selected Persona:** {selected_persona['name']} (ID: {persona_id})")

# Fetch persona details
persona_details_query = supabase.table("personas").select("*").eq("id", persona_id).execute()
if not persona_details_query.data:
    st.error("Persona details not found.")
    st.stop()

persona_details = persona_details_query.data[0]

# Fetch chat history
chat_history = get_chat_history(persona_id)
if not chat_history:
    st.warning("No chat history available for this persona.")
    st.stop()

ai_responses = [entry["content"] for entry in chat_history if entry["role"] == "assistant"]

# Display chat history
st.subheader("💬 Chat History")
for entry in chat_history:
    st.markdown(f"**{entry['role'].capitalize()}:** {entry['content']}")

# Run AI evaluation
async def main():
    await eval_persona_prompt_alignment(persona_details, ai_responses)
    candidate_skills = await eval_candidate_skills(persona_details, chat_history)
    await eval_conversation_success(persona_details, chat_history, candidate_skills)

asyncio.run(main())
