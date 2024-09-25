# /main.py
from flask import Flask, render_template, request
from environment import MultiAgentEnv
from agent import LLMAgent
import yaml

app = Flask(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize environment and agents
env = MultiAgentEnv(config['environment'])
agents = [LLMAgent(i, agent_config['role'], agent_config['tools']) 
          for i, agent_config in enumerate(config['agents'])]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        cycles = int(request.form['cycles'])
        report = run_simulation(task, cycles)
        return render_template('index.html', report=report)
    return render_template('index.html')

def run_simulation(task, cycles):
    env.reset()
    env.task = task
    
    report = f"Task: {task}\n\n"
    conversation_log = []
    
    for cycle in range(cycles):
        report += f"Cycle {cycle + 1}:\n"
        
        # Agent interactions
        for agent in agents:
            context = env._get_observations()[agent.id]
            response = agent.generate_response(task, context)
            report += f"{agent.role}: {response}\n"
            conversation_log.append(f"{agent.role}: {response}")
            
            # Apply action to environment (simplified)
            env.step([0] * env.num_agents)
        
        report += "\n"
    
    # Generate final report
    report += "Final Report:\n"
    for agent in agents:
        report += f"{agent.role} contribution: {agent.generate_response(task, 'Summarize your contribution')}\n"
    
    return report, conversation_log

if __name__ == '__main__':
    app.run(debug=True)
