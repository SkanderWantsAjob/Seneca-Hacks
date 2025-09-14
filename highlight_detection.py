from groq import Groq
import os
from dotenv import load_dotenv
import json


#aaaaaaaaaaaaaaaaaaa333333333
with open("validation.json" , "r") as f:
    data= json.load(f)
    
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

                    {
                    "ID_1": {
                        "duration": <float_seconds>,
                        "timestamps": [[start_1, end_1], [start_2, end_2], ...],
                        "sentences": ["sentence 1", "sentence 2", ...]
                    },
                    ...
                    }

                Your task:

                1. Identify only the most interesting intervals — THIS IS VERY IMPORTANT,
                we only need periods where important events in league of legends(the moba game) especially when there is important deaths or kills or teamfights that are crucial or highlight worthy"
                2. For each interesting interval, provide:
                - `"start"` and `"end"`: the timestamp range of the interval (in seconds),
                - `"reason"`: a concise explanation of why this interval is notable (referencing the sentence content if relevant).
                3. DONT give too much intervals only keep the most important parts, where there is player mistakes and/or deaths
                4. Output strictly as JSON in the following format:
                {
                    "intervals": [
                    {
                        "start": <start_time_in_seconds>,
                        "end": <end_time_in_seconds>,
                        "reason": "<concise_reason_text>"
                    },
                    ...
                    ]
                }

                5. If no interesting interval , return an empty list for `"intervals"`:

                {
                "intervals": []
                }

                6. Prioritize intervals that are **semantically significant or striking** based on content or sentence importance.
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
            stream=False
        )

        content = parse_json_from_string(completion.choices[0].message.content)
        return content  

def main():
    print("Pipeline starting...")
    detector = HighlightDetector()
    highlights_json = detector.detect_highlights(data)
    print(highlights_json)

if __name__ == "__main__":
    main()
