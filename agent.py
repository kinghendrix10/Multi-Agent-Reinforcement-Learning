# /agent.py
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

class LLMAgent:
    def __init__(self, agent_id, role, tools):
        self.id = agent_id
        self.role = role
        self.tools = tools
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    def generate_response(self, task, context):
        prompt = f"Task: {task}\nRole: {self.role}\nTools: {', '.join(self.tools)}\nContext: {context}\nResponse:"
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        
        output = self.model.generate(
            input_ids,
            max_length=100,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def learn(self, knowledge):
        # Simulate learning by updating the agent's knowledge
        pass
