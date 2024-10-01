# agent_network.py

class AgentNetwork:
    def __init__(self):
        self.agents = {}
        self.root_agent = None
        self.next_agent_id = 1
        self.conversation_log = []

    def find_agent_by_name(self, name):
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None

    def add_to_conversation_log(self, message):
        self.conversation_log.append(message)

    def get_conversation_log(self):
        return self.conversation_log
    
    def get_next_agent_id(self):
        agent_id = self.next_agent_id
        self.next_agent_id += 1
        return agent_id

    def add_agent(self, agent):
        self.agents[agent.agent_id] = agent
        if agent.parent is None:
            self.root_agent = agent
        else:
            parent_agent = self.agents.get(agent.parent)
            if parent_agent:
                parent_agent.add_child(agent)
            else:
                raise ValueError(f"Parent agent with ID '{agent.parent}' not found.")

    def update_agent(self, agent):
        self.agents[agent.agent_id] = agent
        # Rebuild the agent hierarchy
        self._rebuild_hierarchy()

    def delete_agent(self, agent_id):
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._rebuild_hierarchy()
        else:
            raise ValueError(f"Agent with ID '{agent_id}' not found.")

    def get_agents(self, exclude_id=None):
        agents = list(self.agents.values())
        if exclude_id:
            agents = [agent for agent in agents if agent.agent_id != exclude_id]
        # Add parent_name to each agent
        for agent in agents:
            parent_agent = self.agents.get(agent.parent)
            agent.parent_name = parent_agent.name if parent_agent else 'None'
        return agents


    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def set_root_instructions(self, instructions):
        if self.root_agent:
            self.root_agent.instructions = instructions
        else:
            raise ValueError("No root agent defined.")

    def execute(self, llm):
        if not self.root_agent:
            raise ValueError("No root agent defined.")
        self.conversation_log = []  # Reset conversation log
        self.root_agent.execute(llm=llm)
    
    # Modify collect_conversation_log to build structured log
    def collect_conversation_log(self):
        self.conversation_log = []
        self._collect_agent_responses(self.root_agent)
        return self.conversation_log

    def _collect_agent_responses(self, agent):
        # Add agent's response to the conversation log
        self.conversation_log.append({
            'sender': 'agent',
            'sender_name': agent.name,
            'text': agent.response,
            'agent_id': agent.agent_id
        })
        # Save parent response for re-execution context
        agent.parent_response = self.agents.get(agent.parent).response if agent.parent else ''
        for child in agent.children:
            self._collect_agent_responses(child)

    def generate_final_report(self):
        report_lines = []
        self._collect_agent_contributions(self.root_agent, report_lines)
        return '\n'.join(report_lines)

    def _collect_agent_contributions(self, agent, report_lines, depth=0):
        indent = "  " * depth
        report_lines.append(f"{indent}- {agent.name} ({agent.role}):")
        response_lines = agent.response.strip().split('\n')
        for line in response_lines:
            report_lines.append(f"{indent}  {line}")
        for child in agent.children:
            self._collect_agent_contributions(child, report_lines, depth + 1)

    def _rebuild_hierarchy(self):
        # Clear current hierarchy
        for agent in self.agents.values():
            agent.children = []
        # Rebuild hierarchy based on parent IDs
        for agent in self.agents.values():
            if agent.parent is None:
                self.root_agent = agent
            else:
                parent_agent = self.agents.get(agent.parent)
                if parent_agent:
                    parent_agent.add_child(agent)
                else:
                    raise ValueError(f"Parent agent with ID '{agent.parent}' not found.")
