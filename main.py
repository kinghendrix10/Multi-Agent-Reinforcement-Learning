# /main.py

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_restful import Api, Resource
from flask_cors import CORS
from agent import LLMAgent
import yaml
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_API_KEY")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
api = Api(app)

agents = {}
agent_counter = 0

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for agent_config in config['agents']:
    agent_id = agent_config.get('id', agent_counter)
    agents[agent_id] = LLMAgent(agent_id, agent_config['name'], agent_config['role'], agent_config['tools'])
    agent_counter += 1

class AgentListResource(Resource):
    def get(self):
        return jsonify([{
            'id': agent.id,
            'name': agent.name,
            'role': agent.role,
            'tools': agent.tools,
        } for agent in agents.values()])

    def post(self):
        global agent_counter
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400
        
        new_agent_id = agent_counter
        agents[new_agent_id] = LLMAgent(new_agent_id, data['name'], data['role'], data['tools'])
        agent_counter += 1
        
        return {'message': 'Agent created', 'agent_id': new_agent_id}, 201

api.add_resource(AgentListResource, '/api/agents')

@socketio.on('connect')
def handle_connect():
    emit('connection_response', {'data': 'Connected to the server'})

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_description = request.form['task']
        cycles = int(request.form['cycles'])
        
        threading.Thread(target=run_simulation, args=(task_description, cycles)).start()
        
    return render_template('index.html', agents=agents.values())

def run_simulation(task_description, cycles):
    conversation_log.clear()
    
    for cycle in range(cycles):
        for agent in agents.values():
            context = "Previous interactions and data"
            response = agent.generate_response(task_description, context)
            conversation_log.append(f"{agent.name} ({agent.role}): {response}")
            agent.learn(task_description, response)
    
    final_report = generate_final_report(task_description)
    
    socketio.emit('task_completed', {'report': final_report})

def generate_final_report(task_description):
    report_lines = ["Final Report:\n"]
    
    for agent in agents.values():
        insights_and_actions = agent.generate_response(task_description, "Summarize your key insights and actions")
        
        report_lines.append(f"{agent.name}'s Contributions:")
        report_lines.append(f"- Role Description: {agent.role}")
        report_lines.append(f"- Tools Used: {', '.join(agent.tools)}")
        report_lines.append(f"- Key Insights and Actions Taken:\n{insights_and_actions}\n")
    
    return "\n".join(report_lines)

if __name__ == '__main__':
    socketio.run(app, debug=True)
