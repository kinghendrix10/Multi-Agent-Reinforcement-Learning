# /agent.py
from llm_model import CerebrasLLM

class LLMAgent:
    def __init__(self, agent_id, name, role, tools):
        self.id = agent_id
        self.name = name
        self.role = role
        self.tools = tools
        self.llm = CerebrasLLM()
        self.knowledge_base = []

    def generate_response(self, task, context):
        system_prompt = f"You are an AI agent named {self.name} with the role of {self.role}. Your tools are: {', '.join(self.tools)}."
        user_prompt = f"Task: {task}\nContext: {context}\nGenerate a response based on your role and tools:"

        return self.llm.generate_response(system_prompt, user_prompt)

    def learn(self, knowledge):
        """
        Learn from new knowledge and update the agent's knowledge base.
        """
        self.knowledge_base.append(knowledge)
        # Optionally, fine-tune the LLM or adjust prompts based on new knowledge