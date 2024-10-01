# agent_network.py

class AgentNetwork:
    def __init__(self):
        self.agents = {}
        self.root_agent = None
        self.next_agent_id = 1

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
        self.root_agent.execute(llm=llm)

    def collect_conversation_log(self):
        log = []
        self._collect_agent_responses(self.root_agent, log)
        return log

    def _collect_agent_responses(self, agent, log):
        log.append(f"{agent.name}: {agent.response}")
        for child in agent.children:
            self._collect_agent_responses(child, log)

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
