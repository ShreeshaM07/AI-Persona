import asyncio
from groq import AsyncGroq
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    print("\n🔍 Persona Evaluation Result:\n", evaluation_result)

async def eval_candidate_skills(persona_details, chat_history):
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    # prompt for skill evaluation
    evaluation_prompt = (
        f"The following conversation is between an AI persona and a candidate. "
        f"The AI persona is role-playing as {persona_details['name']}, who is a {persona_details['occupation']} "
        f"with background in {persona_details['history']}. The candidate is being evaluated based on their responses.\n\n"
        f"### Evaluation Criteria:\n"
        f"1️. **Depth of Knowledge** - Does the candidate show strong understanding and expertise in the concepts?\n"
        f"2️.**Clarity & Communication** - Are their responses well-structured and clear?\n"
        f"3️.**Logical Reasoning** - Do they apply logical thinking to their answers?\n"
        f"4️.**Problem-Solving Ability** - How well do they tackle challenges or tricky questions?\n"
        f"5️.**Confidence & Engagement** - Are they actively engaging or hesitant in responses?\n\n"
        f"Provide a **detailed evaluation** and a **final score (0-100)** based on these factors."
    )

    messages = [{"role": "system", "content": evaluation_prompt}]

    # Append both AI's questions and candidate's responses to the conversation context
    for entry in chat_history:
        role = entry["role"]
        content = entry["content"]

        if role == "assistant":  # AI Persona's questions
            messages.append({"role": "assistant", "content": content})
        elif role == "user":  # Candidate's responses
            messages.append({"role": "user", "content": content})

    messages.append({"role": "user", "content": "Analyze the above conversation and provide a structured skill evaluation with a score (0-100)."})


    response = await client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=512
    )

    evaluation_result = response.choices[0].message.content
    print("\nCandidate Skills Evaluation:\n", evaluation_result)


def get_personas():
    """Fetch all personas from the database."""
    persona_query = supabase.table("personas").select("id, name").execute()
    if not persona_query.data:
        print("No personas found.")
        return []

    return persona_query.data

def get_chat_history(persona_id):
    """Fetch chat history for the selected persona."""
    chat_query = supabase.table("chat_history").select("role, content").eq("persona_id", persona_id).order("timestamp").execute()
    return chat_query.data if chat_query.data else []

# Fetch all personas
personas = get_personas()
if not personas:
    exit()

# Display personas for selection
print("\nAvailable Personas:")
for i, persona in enumerate(personas):
    print(f"{i+1}. {persona['name']} (ID: {persona['id']})")

# User selects persona
choice = int(input("\nSelect a persona by number: ")) - 1
if choice < 0 or choice >= len(personas):
    print("Invalid selection.")
    exit()

selected_persona = personas[choice]
persona_id = selected_persona["id"]

print(f"\n🔹 Selected Persona: {selected_persona['name']} (ID: {persona_id})")

# Fetch persona details
persona_details_query = supabase.table("personas").select("*").eq("id", persona_id).execute()
if not persona_details_query.data:
    print("Persona details not found.")
    exit()

persona_details = persona_details_query.data[0]

# Fetch chat history
chat_history = get_chat_history(persona_id)
ai_responses = [entry["content"] for entry in chat_history if entry["role"] == "assistant"]

if not ai_responses:
    print("No AI responses found for this persona.")
    exit()

# Evaluate persona alignment
asyncio.run(eval_persona_prompt_alignment(persona_details, ai_responses))
# Evaluate candidate skills
asyncio.run(eval_candidate_skills(persona_details, chat_history))
