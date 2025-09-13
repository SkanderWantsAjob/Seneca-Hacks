from groq import Groq
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GROQ_API")

client = Groq(api_key=api_key)

phrases = [
    "11:00: nothing special",
    "11:22: this is amazing",
    "11:23: wow, unbelievable!",
    "11:25: back to normal"
]

data_str = "\n".join(phrases)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": """You are a data analysis assistant. You are given a sequential list of text phrases with timestamps or indices. Your task is:

1. Identify only the most interesting intervals — periods where something truly notable happens, such as sudden excitement, unusual events, spikes in sentiment, or key phrases. Ignore trivial or repetitive text.
2. For each interval, provide a concise explanation of why it is interesting, referring to the content or context.
3. Provide the start and end indices or timestamps of the interval.
4. Stop the interval when the notable event semantically ends, not arbitrarily.
5. Output strictly as JSON with the format:

{{ "intervals": [
    {{
        "start": "timestamp_or_index",
        "end": "timestamp_or_index",
        "reason": "Why this interval is interesting"
    }}
]}}

If no interesting interval exists, return:

{{ "intervals": [] }}

Avoid any commentary or chit-chat outside JSON."""
        },
        {
            "role": "user",
            "content": f"Analyze the following sequential phrases:\n{data_str}"
        }
    ],
    temperature=0,
    top_p=1,
    stream=False
)

result = json.loads(completion.choices[0].message.content)
print(result)
