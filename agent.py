# agent.py
import os
import requests
import serpapi
from dotenv import load_dotenv

load_dotenv()

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
        self.conversation_log = []
        
    def add_child(self, child_agent):
        self.children.append(child_agent)

    def execute(self, task="", context="", llm=None):
        # Generate the agent's response using the LLM
        system_prompt = f"You are an AI agent with the role of {self.role}."
        user_prompt = f"{self.instructions}\nTask: {task}\nContext: {context}"
        conversation_history = self.get_conversation_history()
        user_prompt += f"\nConversation History:\n{conversation_history}"

        if "web_search" in self.instructions.lower():
            search_results = self.web_search(query=task)
            user_prompt += f"\nWeb Search Results:\n{search_results}"

        if llm:
            self.response = llm.generate_response(system_prompt, user_prompt)
        else:
            self.response = "Default response without LLM."
        
        # Save the context for potential re-execution
        self.parent_response = context

        # Add the agent's response to the conversation log
        self.conversation_log.append({
            'sender': self.name,
            'text': self.response,
            'agent_id': self.agent_id
        })
        
        # Execute child agents with the current agent's response as context
        for child in self.children:
            child.conversation_log = self.conversation_log.copy()
            child.execute(task=task, context=self.response, llm=llm)

    def update_parameters(self, **kwargs):
        self.parameters.update(kwargs)

    def process_user_feedback(self, feedback, llm=None):
        # Update instructions or context based on feedback
        self.instructions += f"\nUser Feedback: {feedback}"
        # Re-execute the agent with the new instructions
        self.execute(context=self.parent_response, llm=llm)

    def web_search(self, query, num_results=3):
        api_key = os.environ.get("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("SERPAPI_API_KEY is not set in the environment variables.")

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": num_results
        }

        try:
            search = serpapi.search(params)
            results = search.get_dict()

            # Extract desired results
            result_keys = ["organic_results", "results", "answer_box", "knowledge_graph"]
            for key in result_keys:
                if key in results:
                    extracted_results = results[key]
                    break
            else:
                extracted_results = []

            formatted_results = []
            for r in extracted_results:
                formatted_result = {
                    "title": r.get("title", "No title"),
                    "link": r.get("link", r.get("url", "No link")),
                    "snippet": r.get("snippet", r.get("description", r.get("summary", "No snippet available")))
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            print(f"Error during web search: {e}")
            return []

    def get_conversation_history(self):
        # Retrieve and format the conversation history
        history = ""
        for message in self.conversation_log:
            history += f"{message['sender']}: {message['text']}\n"
        return history
    
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

    def process_user_feedback(self, feedback, llm=None):
        # Incorporate user preferences into the report
        self.instructions += f"\nUser Preferences: {feedback}"
        self.execute(agents_data=self.agents_data, llm=llm)

    def finalize_report(self):
        # Perform any final processing
        self.is_finalized = True