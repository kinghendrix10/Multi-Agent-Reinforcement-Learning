# /agent.py
from llm_model import CerebrasLLM

class LLMAgent:
    def __init__(self, agent_id, role, tools):
        self.id = agent_id
        self.role = role
        self.tools = tools
        self.llm = CerebrasLLM()

    def generate_response(self, task, context):
        system_prompt = f"You are an AI agent with the role of {self.role}. Your tools are: {', '.join(self.tools)}."
        user_prompt = f"Task: {task}\nContext: {context}\nGenerate a response based on your role and tools:"
        
        return self.llm.generate_response(system_prompt, user_prompt)

    def learn(self, knowledge):
        # Simulate learning by updating the agent's knowledge
        pass