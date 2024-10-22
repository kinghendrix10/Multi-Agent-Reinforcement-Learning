# agent_network.py

import asyncio
from backend.agent import Agent

class AgentNetwork:
    def __init__(self):
        self.agents = {}
        self.root_agents = []
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
        if agent.parent_id is None:
            self.root_agents.append(agent)  # Corrected line
        else:
            parent_agent = self.agents.get(agent.parent_id)
            if parent_agent:
                parent_agent.add_child(agent)
            else:
                raise ValueError(f"Parent agent with ID '{agent.parent_id}' not found.")

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
            parent_agent = self.agents.get(agent.parent_id)
            agent.parent_name = parent_agent.name if parent_agent else 'None'
        return agents

    def get_agent(self, agent_id):
        return self.agents.get(int(agent_id))

    def execute(self, llm, task):
        # Asynchronous execution of root agents
        self.conversation_log = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [root_agent.async_execute(task=task, llm=llm) for root_agent in self.root_agents]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    def collect_conversation_log(self):
        self.conversation_log = []
        for root_agent in self.root_agents:
            self._collect_agent_responses(root_agent)
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
        agent.parent_response = self.agents.get(agent.parent_id).response if agent.parent_id else ''
        for child in agent.children:
            self._collect_agent_responses(child)

    def get_agents_responses(self):
        responses = ""
        for agent in self.agents.values():
            # Exclude the report agent if it's in the agents list
            if agent.agent_id != 9999:
                responses += f"Agent {agent.name} ({agent.role}):\n{agent.response}\n\n"
        return responses

    def _rebuild_hierarchy(self):
        # Clear current hierarchy
        for agent in self.agents.values():
            agent.children = []
        # Clear root agents list
        self.root_agents = []
        # Rebuild hierarchy based on parent IDs
        for agent in self.agents.values():
            if agent.parent_id is None:
                self.root_agents.append(agent)  # Corrected line
            else:
                parent_agent = self.agents.get(agent.parent_id)
                if parent_agent:
                    parent_agent.add_child(agent)
                else:
                    raise ValueError(f"Parent agent with ID '{agent.parent_id}' not found.")
