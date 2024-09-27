# /main.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_restful import Api, Resource
from agent import LLMAgent
import yaml
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
api = Api(app)

# In-memory storage for agents
agents = {}
agent_counter = 0

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize agents from config
for agent_config in config['agents']:
    agent_id = agent_config.get('id')
    if agent_id is None:
        agent_id = agent_counter
        agent_counter += 1
    else:
        agent_counter = max(agent_counter, agent_id + 1)
    agent = LLMAgent(agent_id, agent_config['name'], agent_config['role'], agent_config['tools'])
    agents[agent_id] = agent

# RESTful API Endpoints
class AgentListResource(Resource):
    def get(self):
        return jsonify([
            {
                'id': agent.id,
                'name': agent.name,
                'role': agent.role,
                'tools': agent.tools
            } for agent in agents.values()
        ])

    def post(self):
        global agent_counter
        data = request.get_json()
        if data is None:
            return {'message': 'No input data provided'}, 400

        agent_id = agent_counter
        agent_counter += 1
        agent = LLMAgent(agent_id, data['name'], data['role'], data['tools'])
        agents[agent_id] = agent
        return {'message': 'Agent created', 'agent_id': agent_id}, 201

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
        if data is None:
            return {'message': 'No input data provided'}, 400

        agent = agents.get(agent_id)
        if not agent:
            return {'message': 'Agent not found'}, 404
        agent.name = data.get('name', agent.name)
        agent.role = data.get('role', agent.role)
        agent.tools = data.get('tools', agent.tools)
        return {'message': 'Agent updated'}

    def delete(self, agent_id):
        agent = agents.get(agent_id)
        if agent:
            del agents[agent_id]
            return {'message': 'Agent deleted'}
        else:
            return {'message': 'Agent not found'}, 404

api.add_resource(AgentListResource, '/api/agents')
api.add_resource(AgentResource, '/api/agents/<int:agent_id>')

# Task Queue
task_queue = []
conversation_log = []

def process_tasks():
    while task_queue:
        task = task_queue.pop(0)
        run_simulation(task['task'], task['cycles'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        cycles = int(request.form['cycles'])
        # Add task to the queue
        task_queue.append({'task': task, 'cycles': cycles})
        # Start task processing in a separate thread
        threading.Thread(target=process_tasks).start()
        return render_template('index.html', agents=agents.values(), report="Task is being processed.", conversation_log=conversation_log)
    return render_template('index.html', agents=agents.values())

def run_simulation(task, cycles):
    global conversation_log
    conversation_log = []
    report = f"Task: {task}\n\n"

    for cycle in range(cycles):
        report += f"Cycle {cycle + 1}:\n"

        # Agent interactions
        for agent in agents.values():
            context = "Previous interactions and data"
            response = agent.generate_response(task, context)
            conversation_log.append(f"{agent.name} ({agent.role}): {response}")

            # Agents learn from each other's responses
            agent.learn(response)

        report += "\n"

    # Generate final report
    final_report = generate_final_report(task)
    socketio.emit('task_completed', {'report': final_report, 'conversation_log': conversation_log})

def generate_final_report(task):
    report = "Final Report:\n\n"

    for agent in agents.values():
        context_summary = "Summarize your key insights and actions"
        insights_and_actions = agent.generate_response(task, context_summary)

        report += f"{agent.name}'s Contributions:\n"
        report += f"- Role Description: {agent.role}\n"
        report += f"- Tools Used: {', '.join(agent.tools)}\n"
        report += f"- Key Insights and Actions Taken:\n"
        report += f"   {insights_and_actions}\n\n"

    return report

@socketio.on('connect')
def handle_connect():
    emit('connection_response', {'data': 'Connected to the server'})

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

if __name__ == '__main__':
    socketio.run(app, debug=True)