from groq import Groq
import os
from dotenv import load_dotenv
import json

import re

def parse_json_from_string(s: str):
    start = s.find("{")
    end = s.rfind("}") + 1  # include last '}'

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in string.")

    json_str = s[start:end]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    

load_dotenv()
api_key = os.getenv("GROQ_API")

client = Groq(api_key=api_key)



class HighlightDetector:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.model = model
    
    def detect_highlights(self, batch):
        """
        Send batch (captions + timestamps) to LLM and return highlight JSON.
        """
        prompt = """You are a data analysis assistant. You are given a dataset in the following structure:

                    [
                        {
                            "text": <caption_text>,
                            "start": <float_seconds>,
                            "end": <float_seconds>
                        },
                    ]
                Your task:

                1.this is a league of legends(the moba game) official Match.
                Identify only the most interesting intervals where highlight worthy moments happen — THIS IS VERY IMPORTANT,
                We want something Spectators want to see, something with action.
                don't be too picky or too broad.
                Important events are such as:
                    players making errors and dying
                    the start of Impressive plays
                    the start of important deaths or kills
                    teamfights that are crucial and/or ACES (when the whole team is wiped out)
                    stealing objectives from the other team( dragon/baron/elder/herald/voidgrubs)
                DO NOT consider events like:
                    farming
                    taking jungle camps
                    backing to base
                    doing objectives that are not contested
                    discussing strategy
                    anticlimactic fights
                    minor skirmishes that don't lead to significant outcomes
                DONT consider Analytics please and DONT consider events that are just setting up for a fight or potential action, Only consider the actual action.
                2. For each interesting interval, provide:
                - `"start"` and `"end"`: the timestamp range of the interval (in seconds),
                - `"reason"`: a concise explanation of why this interval is notable (referencing the sentence content if relevant).
                4. Output strictly AND ONLY as JSON in the following format:
                {
                    "intervals": [
                    {
                        "start": <start_time_in_seconds>,
                        "end": <end_time_in_seconds>,
                        "reason": "<concise_reason_text>"
                    }
                    ]
                }
                5.if there is multiple interesting events close to each other, take only the last event.
                6.if There is a death we want to see a bit before the death.

                7. If no interesting interval , return an empty list for `"intervals"`:

                {
                "intervals": []
                }

                8. Prioritize intervals that are **semantically significant or striking** based on content or sentence importance.
                9. no more than 25 seconds per highlight and at least 10 seconds.
                """

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system","content": prompt},
                {
                    "role": "user",
                    "content": f"Analyze the following sequential phrases:\n{batch}"
                }
            ],
            temperature=0,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"}
        )

        content = parse_json_from_string(completion.choices[0].message.content)
        return content

