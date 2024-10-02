# agent.py

class Agent:
    def __init__(self, agent_id, name, role, instructions, parent=None):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.instructions = instructions
        self.parent = parent  # Parent agent ID
        self.children = []    # List of child Agent instances
        self.response = None
        self.parent_response = ''  # Store parent's response for context

    def add_child(self, child_agent):
        self.children.append(child_agent)

    def execute(self, task="", context="", llm=None):
        # Generate the agent's response using the LLM
        system_prompt = f"You are an AI agent with the role of {self.role}."
        user_prompt = f"{self.instructions}\nTask: {task}\nContext: {context}"
        
        if llm:
            self.response = llm.generate_response(system_prompt, user_prompt)
        else:
            self.response = "Default response without LLM."
        
        # Save the context for potential re-execution
        self.parent_response = context
        
        # Execute child agents with the current agent's response as context
        for child in self.children:
            child.execute(task=task, context=self.response, llm=llm)


    def to_dict(self):
        return {
            'id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'instructions': self.instructions,
            'parent': self.parent
        }


class ReportAgent(Agent):
    def __init__(self, agent_id, name, role, instructions):
        super().__init__(agent_id, name, role, instructions)
        self.response = None

    def execute(self, agents_data, llm=None):
        # Generate the report using the LLM
        system_prompt = f"You are {self.role}."
        user_prompt = f"{self.instructions}\n\nHere are the findings from other agents:\n{agents_data}"

        if llm:
            self.response = llm.generate_response(system_prompt, user_prompt)
        else:
            self.response = "Default report without LLM."