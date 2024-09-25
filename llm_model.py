# /llm_model.py
import os
from cerebras.cloud.sdk import Cerebras

class CerebrasLLM:
    def __init__(self):
        self.client = Cerebras(
            api_key=os.environ.get("CEREBRAS_API_KEY")
        )

    def generate_response(self, system_prompt, user_prompt):
        stream = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama3.1-70b",
            stream=True,
            max_tokens=1024,
            temperature=1,
            top_p=1
        )

        response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                response += content

        return response

# Usage example:
if __name__ == "__main__":
    llm = CerebrasLLM()
    system_prompt = "You are a helpful AI assistant."
    user_prompt = "What is the capital of France?"
    response = llm.generate_response(system_prompt, user_prompt)
    print(response)
