# llm_model.py

import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

class LLM:
    def __init__(self):
        self.client = Cerebras(
            api_key=os.environ.get("CEREBRAS_API_KEY")
        )

    def generate_response(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3.1-70b",
            stream=False,
            max_tokens=1024,
            temperature=1,
            top_p=1
        )
        return response.choices[0].message.content

# Implement rate limiting for the LLM API