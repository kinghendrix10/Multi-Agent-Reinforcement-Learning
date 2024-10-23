# llm_model.py

import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
import json
import dspy

load_dotenv()

lm = dspy.LM('groq/llama3-70b-8192', api_key=os.environ.get("GROQ_API_KEY"), temperature=0, max_tokens=8000)
dspy.configure(lm=lm)

# Define a signature for team generation
class TeamGenerationSignature(dspy.Signature):
    task_description = dspy.InputField()
    team = dspy.OutputField(desc="JSON array of agents, roles, instructions and parent_id")

# Define a module for team generation
class TeamGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_team = dspy.ChainOfThought(TeamGenerationSignature)

    def forward(self, task_description):
        result = self.generate_team(task_description=task_description)
        return result.team
    
class LLM:
    def __init__(self):
        self.client = Cerebras(
            api_key=os.environ.get("CEREBRAS_API_KEY")
        )

    def generate_response(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3.1-70b",
            stream=False,
            max_tokens=1024,
            temperature=1,
            top_p=1
        )
        return response.choices[0].message.content

    def generate_agent_team(self, task_description):

        team_generator = TeamGenerator()
        system_prompt = "You are an AI that designs teams of agents to solve tasks."
        user_prompt = f"""Design a team of agents to accomplish the following task:

    {task_description}

    Provide the team as a JSON array. Each agent should be a JSON object with the following fields:
    - "name": A unique name for the agent. must not have space " " instead use "_" such "Business_Analyst" or "BusinessAnalyst" and not "Business Analyst".
    - "role": A brief description of the agent's role.
    - "instructions": Detailed instructions for the agent.
    - "parent_id": The name of the parent agent (if any), or null for root agents.

    Example:
    [
        {{
            "agent": "Business_Analyst",
            "role": "An experienced business analyst with a keen eye for market opportunities and potential pitfalls",
            "instructions": "As an expert business analyst, evaluate the given business idea. Assess its viability, potential, and uniqueness in the market. Identify key strengths, weaknesses, opportunities, and threats. Provide an objective analysis of the idea, potential for success, and any areas that need improvement.",
            "parent_id": null
        }},
        {{
            "agent": "Market_Research",
            "role": "A data-driven market research specialist with extensive knowledge of various industries and market trends.",
            "instructions": "As a seasoned market research specialist, conduct a comprehensive market analysis for the given business idea. Determine the Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM). Identify key market trends, growth potential, and competitive landscape. Provide data-backed insights to support your analysis.",
            "parent_id": "Business_Analyst"
        }}
    ]

    Now, please provide the agent team for the task.
    """

        # Generate the team using the LLM
        response = team_generator(task_description=task_description)

        # Parse the response as JSON
        try:
            agent_definitions = json.loads(response)
        except json.JSONDecodeError as e:
            # Handle parsing error
            print(f"Error parsing agent definitions from LLM response: {e}")
            agent_definitions = []
            # Optionally, you can re-prompt the LLM or notify the user

        return agent_definitions
