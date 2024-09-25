# /main.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from environment import MultiAgentEnv
from agent import LLMAgent
import yaml

app = Flask(__name__)
socketio = SocketIO(app)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize agents
agents = [LLMAgent(i, agent_config['role'], agent_config['tools']) 
          for i, agent_config in enumerate(config['agents'])]

# Register and initialize environment
env = MultiAgentEnv(config['environment'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        cycles = int(request.form['cycles'])
        report, conversation_log = run_simulation(task, cycles)
        return render_template('index.html', agents=agents, report=report, conversation_log=conversation_log)
    return render_template('index.html', agents=agents)

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
            conversation_log.append(f"{agent.role}: {response}")
            
            # Apply action to environment (simplified)
            env.step([0] * env.num_agents)
        
        report += "\n"
    
    # Generate final report
    final_report = generate_final_report(task)
    return final_report, conversation_log

def generate_final_report(task):
    report = "Final Report:\n\n"
    
    for agent in agents:
        context_summary = "Summarize your key insights and actions"
        insights_and_actions = agent.generate_response(task, context_summary)
        
        report += f"{agent.role}'s Contributions:\n"
        report += f"- Role Description: {agent.role}\n"
        report += f"- Tools Used: {', '.join(agent.tools)}\n"
        report += f"- Key Insights and Actions Taken:\n"
        report += f"   {insights_and_actions}\n\n"
    
    return report

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

if __name__ == '__main__':
    socketio.run(app, debug=True)