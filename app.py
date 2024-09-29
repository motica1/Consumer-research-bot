from langsmith import traceable
from dotenv import load_dotenv
import chainlit as cl
import openai
import os
import asyncio
from prompts import ASSESSMENT_PROMPT, SYSTEM_PROMPT
from functions import get_wirecutter_reviews

# Load environment variables
load_dotenv()

configurations = {
    "openai_gpt-4": {
        "endpoint_url": os.getenv("OPENAI_ENDPOINT"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4"
    }
}

# Choose configuration
config_key = "openai_gpt-4"

# Get selected configuration
config = configurations[config_key]

# Initialize the OpenAI async client
client = openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"])

gen_kwargs = {
    "model": config["model"],
    "temperature": 0.3,
    "max_tokens": 500
}

@cl.on_chat_start
def on_chat_start():    
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    cl.user_session.set("message_history", message_history)

@traceable
async def assess_message():

    print("Assessing message")
    functions = [
        {
            "name": "get_wirecutter_reviews",
            "description": "Get reviews from the Wirecutter website.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for."
                    }
                },
                "required": ["keyword"]
            }
        }
    ]

    
    # Generate the response
    response = await client.chat.completions.create(
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        functions=functions,
        function_call="auto", 
        **gen_kwargs)

    print("Response: ", response)
    output = response.choices[0].message.content.strip()
    print("Output: ", output)

    if "reviews" in output.lower():
        keyword = output.split("reviews")[1].strip()
        reviews = await get_wirecutter_reviews(keyword)
        return reviews

@traceable
@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history", [])    

    message_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    message_history.append({"role": "user", "content": message.content})

    message_history.append({"role": "system", "content": await assess_message()})

    response_message = cl.Message(content="")
    await response_message.send()

    if config_key == "mistral_7B":
        stream = await client.completions.create(prompt=message.content, stream=True, **gen_kwargs)
        async for part in stream:
            if token := part.choices[0].text or "":
                await response_message.stream_token(token)
    else:
        # Filter out messages with null content
        valid_messages = [msg for msg in message_history if msg.get("content") is not None]
        stream = await client.chat.completions.create(messages=valid_messages, stream=True, **gen_kwargs)
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await response_message.stream_token(token)

    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)
    await response_message.update()

if __name__ == "__main__":
    cl.main()