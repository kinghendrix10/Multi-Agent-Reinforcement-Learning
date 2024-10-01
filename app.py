# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
from agent import Agent
from agent_network import AgentNetwork
from llm_model import LLM 
import os
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize agent network
agent_network = AgentNetwork()

# Load agents from configuration (if exists)
if os.path.exists('config.yaml'):
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        # Load agents from configuration
        for agent_config in config.get('agents', []):
            agent = Agent(
                agent_id=agent_config['id'],
                name=agent_config['name'],
                role=agent_config['role'],
                instructions=agent_config['instructions'],
                parent=agent_config.get('parent')
            )
            agent_network.add_agent(agent)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        run_simulation(task)
        conversation_log = agent_network.get_conversation_log()
        report = agent_network.generate_final_report()
        return render_template(
            'index.html',
            agents=agent_network.get_agents(),
            report=report,
            conversation_log=conversation_log,
            agent_network=agent_network
        )
    return render_template('index.html', agents=agent_network.get_agents(), agent_network=agent_network)

@app.route('/manage_agents', methods=['GET'])
def manage_agents():
    agents = agent_network.get_agents()
    return render_template('manage_agents.html', agents=agents, agent_network=agent_network)

@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.form
    agent = Agent(
        agent_id=agent_network.get_next_agent_id(),
        name=data['name'],
        role=data['role'],
        instructions=data['instructions'],
        parent=int(data['parent']) if data['parent'] != 'None' else None
    )
    agent_network.add_agent(agent)
    return redirect(url_for('manage_agents'))

@app.route('/edit_agent/<int:agent_id>', methods=['GET', 'POST'])
def edit_agent(agent_id):
    agent = agent_network.get_agent(agent_id)
    if request.method == 'POST':
        data = request.form
        agent.name = data['name']
        agent.role = data['role']
        agent.instructions = data['instructions']
        agent.parent = int(data['parent']) if data['parent'] != 'None' else None
        agent_network.update_agent(agent)
        return redirect(url_for('manage_agents'))
    parents = agent_network.get_agents(exclude_id=agent_id)
    return render_template('edit_agent.html', agent=agent, parents=parents, agent_network=agent_network)

@app.route('/delete_agent/<int:agent_id>', methods=['POST'])
def delete_agent(agent_id):
    agent_network.delete_agent(agent_id)
    return redirect(url_for('manage_agents'))

def run_simulation(task):
    llm = LLM()  # Initialize your LLM client
    agent_network.set_root_instructions(task)  # Set the task as the root agent's instructions
    agent_network.execute(llm=llm)

    # Collect responses
    conversation_log = agent_network.collect_conversation_log()
    report = agent_network.generate_final_report()

    return report, conversation_log

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    conversation_log = request.json.get('conversation_log', '')
    with open('conversation_log.txt', 'w') as f:
        f.write(conversation_log)
    return {'status': 'success'}

@app.route('/save_report', methods=['POST'])
def save_report():
    report = request.json.get('report', '')
    with open('report.txt', 'w') as f:
        f.write(report)
    return {'status': 'success'}

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '')
    response = {'status': 'error'}

    # Detect if the message contains an agent tag
    if '@' in message:
        # Extract agent name
        parts = message.split()
        tagged_agents = [part[1:] for part in parts if part.startswith('@')]
        for agent_name in tagged_agents:
            # Find the agent by name
            agent = agent_network.find_agent_by_name(agent_name)
            if agent:
                # Re-execute the agent's task
                llm = LLM()
                agent.execute(context=agent.parent_response, llm=llm)
                # Update conversation log
                agent_network.add_to_conversation_log({
                    'sender': agent.name,
                    'sender_name': agent.name,
                    'text': agent.response,
                    'agent_id': agent.agent_id
                })
                response = {
                    'status': 'success',
                    'response': agent.response,
                    'agent_name': agent.name,
                    'agent_id': agent.agent_id
                }
                break
            else:
                response = {'status': 'error', 'message': f'Agent "{agent_name}" not found.'}
    else:
        response = {'status': 'error', 'message': 'No agent tagged.'}

    return jsonify(response)

if __name__ == '__main__':
    socketio.run(app, debug=True)
