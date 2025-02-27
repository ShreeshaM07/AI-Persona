import asyncio
from groq import AsyncGroq

async def get_ai_response(persona_background, chat_history, user_input):
    client = AsyncGroq(
        api_key='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',
    )

    # Construct a detailed persona description
    persona_details = (
        f"Do not say that you are an AI agent. You are actually a person."
        f"You are role-playing as {persona_background['name']}. "
        f"You are a {persona_background['age']}-year-old {persona_background['gender']} "
        f"from {persona_background['location']}. You work as a {persona_background['occupation']}. "
        f"You have a background in {persona_background['education']}. "
        f"Your personality traits include being {persona_background['traits']}. So behave and answer in a similar way. "
        f"Your communication style is {persona_background['communication_style']}. "
        f"Your history includes: {persona_background['history']}."
        f"Answer the questions to the point do not beat around the bush. Keep it as relevant as possible."
    )

    messages = [
        {"role": "system", "content": persona_details},
    ]

    # Append chat history
    messages.extend(chat_history)

    # Add user input
    messages.append({"role": "user", "content": user_input})

    # Call the Groq API
    response = await client.chat.completions.create(
        messages=messages,
        model="mixtral-8x7b-32768",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=True
    )

    # Collect AI response
    ai_response = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:  # Ensure it's not None
            ai_response += chunk.choices[0].delta.content


    return ai_response
