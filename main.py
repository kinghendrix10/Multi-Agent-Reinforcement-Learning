# /main.py

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_restful import Api, Resource
from flask_cors import CORS
from agent import LLMAgent
import yaml
import threading
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_API_KEY")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
api = Api(app)

agents = {}
agent_counter = 0
task_queue = []
conversation_log = []

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize agents from config
for agent_config in config['agents']:
    agent_id = agent_config.get('id', agent_counter)
    agent_counter = max(agent_counter, agent_id + 1)
    agent = LLMAgent(agent_id, agent_config['name'], agent_config['role'], agent_config['tools'])
    agents[agent_id] = agent

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

class AgentResource(Resource):
    def get(self, agent_id):
        agent = agents.get(agent_id)
        if not agent:
            return {'message': 'Agent not found'}, 404
        return {
            'id': agent.id,
            'name': agent.name,
            'role': agent.role,
            'tools': agent.tools
        }

    def put(self, agent_id):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400
        agent = agents.get(agent_id)
        if not agent:
            return {'message': 'Agent not found'}, 404
        agent.name = data.get('name', agent.name)
        agent.role = data.get('role', agent.role)
        agent.tools = data.get('tools', agent.tools)
        return {'message': 'Agent updated'}

    def delete(self, agent_id):
        if agent_id in agents:
            del agents[agent_id]
            return {'message': 'Agent deleted'}
        return {'message': 'Agent not found'}, 404

api.add_resource(AgentListResource, '/api/agents')
api.add_resource(AgentResource, '/api/agents/<int:agent_id>')

def process_tasks():
    while task_queue:
        task = task_queue.pop(0)
        run_simulation(task['task'], task['cycles'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        cycles = int(request.form['cycles'])
        task_queue.append({'task': task, 'cycles': cycles})
        threading.Thread(target=process_tasks).start()
        return render_template('index.html', agents=agents.values(), report="Task is being processed.", conversation_log=conversation_log)
    return render_template('index.html', agents=agents.values())

def run_simulation(task, cycles):
    global conversation_log
    conversation_log.clear()
    
    for cycle in range(cycles):
        for agent in agents.values():
            context = "Previous interactions and data"
            response = agent.generate_response(task, context)
            conversation_log.append(f"{agent.name} ({agent.role}): {response}")
            agent.learn(task, response)
    
    final_report = generate_final_report(task)
    socketio.emit('task_completed', {'report': final_report, 'conversation_log': conversation_log})

def generate_final_report(task):
    report_lines = ["Final Report:\n"]
    
    for agent in agents.values():
        insights_and_actions = agent.generate_response(task, "Summarize your key insights and actions")
        
        report_lines.append(f"{agent.name}'s Contributions:")
        report_lines.append(f"- Role Description: {agent.role}")
        report_lines.append(f"- Tools Used: {', '.join(agent.tools)}")
        report_lines.append(f"- Key Insights and Actions Taken:\n{insights_and_actions}\n")
    
    return "\n".join(report_lines)

@app.route('/agents')
def agents_page():
    return render_template('agents.html')

@app.route('/tasks')
def tasks_page():
    return render_template('tasks.html')

@app.route('/conversations')
def conversation_page():
    return render_template('conversation.html')

class ConversationResource(Resource):
    def get(self):
        return jsonify(conversation_log)

api.add_resource(ConversationResource, '/api/conversations')

@socketio.on('connect')
def handle_connect():
    emit('connection_response', {'data': 'Connected to the server'})

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

if __name__ == '__main__':
    socketio.run(app, debug=True)