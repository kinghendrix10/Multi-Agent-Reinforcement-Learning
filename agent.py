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

    def learning_transfer_function(self, new_knowledge):
        system_prompt = f"You are an AI agent named {self.name} with the role of {self.role}."
        user_prompt = f"New Knowledge: {new_knowledge}\nSummarize and extract key information to update your knowledge base:"
        summary = self.llm.generate_response(system_prompt, user_prompt)
        self.knowledge_base.append(summary)

    def learn(self, task, knowledge):
        system_prompt = f"You are an AI agent named {self.name} with the role of {self.role}. Your tools are: {', '.join(self.tools)}."
        user_prompt = f"Task: {task}\nNew Knowledge: {self.learning_transfer_function(knowledge)}\nUpdate your knowledge base and provide a summary of what you've learned:"
        learning_summary = self.llm.generate_response(system_prompt, user_prompt)
        self.knowledge_base.append(learning_summary)
        return learning_summary
