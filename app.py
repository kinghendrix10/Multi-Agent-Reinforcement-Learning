# app.py

import asyncio
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_file, flash
from flask_socketio import SocketIO, emit
from agent import Agent, ReportAgent
from agent_network import AgentNetwork
from llm_model import LLM 
import os
import json
import io
import re
import pdfkit
from docx import Document
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
socketio = SocketIO(app)
llm = LLM()
# Initialize agent network
agent_network = AgentNetwork()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form['task']
        if not agent_network.agents:
            # No agents have been created; execute the report agent directly
            report, conversation_log = run_simulation(task, no_agents=True)
        else:
            # Agents exist; proceed with running the simulation
            report, conversation_log = run_simulation(task)
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
    return render_template('manage_agents.html', agents=agents, agent_network=agent_network, report_agent=report_agent)

@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.form
    agent = Agent(
        agent_id=agent_network.get_next_agent_id(),
        name=data['name'],
        role=data['role'],
        instructions=data['instructions'],
        parent_id=int(data['parent_id']) if data['parent_id'] != 'None' else None
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
        agent.parent_id = int(data['parent_id']) if data['parent_id'] != 'None' else None
        agent_network.update_agent(agent)
        return redirect(url_for('manage_agents'))
    parents = agent_network.get_agents(exclude_id=agent_id)
    return render_template('edit_agent.html', agent=agent, parents=parents, agent_network=agent_network)

@app.route('/delete_agent/<int:agent_id>', methods=['POST'])
def delete_agent(agent_id):
    agent = agent_network.get_agent(agent_id)
    if not agent:
        return "Agent not found", 404
    agent_network.delete_agent(agent_id)
    return redirect(url_for('manage_agents'))

@app.route('/edit_report_agent', methods=['GET', 'POST'])
def edit_report_agent():
    if request.method == 'POST':
        data = request.form
        report_agent.name = data['name']
        report_agent.role = data['role']
        report_agent.instructions = data['instructions']
        return redirect(url_for('manage_agents'))
    return render_template('edit_report_agent.html', agent=report_agent)

report_agent = ReportAgent(
    agent_id=9999,  # Use a unique ID that doesn't conflict with other agents
    name="ReportAgent",
    role="A skilled writer, you generate reports with a detailed overview of the task.",
    instructions="""As a skilled analyst and writer, generate a comprehensive report.
    Structure the report with clear sections and appropriate headings, introduction, body, and actionable conclusions.
    Utilize appropriate data analysis techniques, metrics, and writing styles to effectively communicate insights and recommendations.
    if no other agents are present, generate a report based on the task instructions Adapt your approach to be concise and professional.
    Else, compile data and insights from all other agents, Ensure the report is clear, concise, and professional.
    Adapt the depth and breadth of your analysis to your understanding of the problem."""
) 

@app.route('/api/agents/network', methods=['GET'])
def get_agent_network():
    nodes = []
    edges = []
    for agent in agent_network.agents.values():  # Corrected line
        nodes.append({
            'id': agent.agent_id,
            'label': agent.name,
            'title': agent.role
        })
        if agent.parent_id:
            edges.append({
                'from': agent.parent_id,
                'to': agent.agent_id
            })
    return jsonify({'nodes': nodes, 'edges': edges})

def run_simulation(task, no_agents=False):
    llm = LLM()  # Initialize your LLM client
    if no_agents:
        # No agents; execute the report agent directly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(report_agent.execute(agents_data=None, llm=llm, task=task))
        loop.close()
        report = report_agent.response
        conversation_log = []
    else:
        # Agents exist; proceed with executing them
        agent_network.execute(llm=llm, task=task)
        # Collect responses
        conversation_log = agent_network.collect_conversation_log()
        print(conversation_log)
        agents_data = agent_network.get_agents_responses()
        print(agents_data)
        # Execute the report agent with agents' data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(report_agent.execute(agents_data=agents_data, llm=llm))
        loop.close()
        report = report_agent.response
    # Emit the new report to the frontend
    socketio.emit('update_report', {'report': report})
    return report, conversation_log


def extract_tagged_agents(message):
    # Use regex to find all words starting with '@'
    tagged_agents = re.findall(r'@(\w+)', message)
    return [tag.strip() for tag in tagged_agents]

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

@app.route('/report')
def report():
    # Assuming you have a variable 'agent' representing the reporting agent
    report_content = agent.generate_report()
    diagram_definition = agent.diagram_definition
    return render_template('report.html', report=report_content, diagram_definition=diagram_definition)

@app.route('/finalize_report', methods=['POST'])
def finalize_report():
    report_agent.finalize_report()
    # Optionally, prevent further edits or agent updates
    return jsonify({'status': 'success', 'message': 'Report finalized.'})

@socketio.on('message')
def handle_message(message):
    emit('response', {'data': f'Received: {message}'})

@app.route('/send_message', methods=['POST'])
def send_message():
    print("Received message request")
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    message = data.get('message', '')
    response = {'status': 'error'}

    tagged_agents = extract_tagged_agents(message)

    if tagged_agents:
        for agent_name in tagged_agents:
            agent = agent_network.find_agent_by_name(agent_name)
            if agent:
                try:
                    # Process user feedback or new instructions
                    agent.process_user_feedback(message, llm=llm)
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
                except Exception as e:
                    print(f"Error processing feedback: {e}")
                    response = {'status': 'error', 'message': 'An error occurred while processing the message.'}
            else:
                response = {'status': 'error', 'message': f'Agent "{agent_name}" not found.'}
    else:
        response = {'status': 'error', 'message': 'No agent tagged.'}

    return jsonify(response)

@app.route('/agent_network')
def view_agent_network():
    return render_template('agent_network.html')

@app.route('/export_report', methods=['GET'])
def export_report():
    format = request.args.get('format')
    report_content = report_agent.response

    if format == 'pdf':
        # Convert to PDF
        pdf = pdfkit.from_string(report_content, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response
    elif format == 'word':
        # Convert to Word document
        document = Document()
        document.add_paragraph(report_content)
        f = io.BytesIO()
        document.save(f)
        f.seek(0)
        return send_file(f, as_attachment=True, attachment_filename='report.docx')
    elif format == 'markdown':
        # Convert to Markdown file
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/markdown'
        response.headers['Content-Disposition'] = 'attachment; filename=report.md'
        return response
    else:
        return jsonify({'status': 'error', 'message': 'Invalid format'})

@app.route('/generate_agents', methods=['POST'])
def generate_agents():
    task = request.form.get('task', 'Create a team of agents to solve the problem.')
    llm = LLM()

    # Generate agent team using the LLM
    agent_definitions = llm.generate_agent_team(task)
    print(agent_definitions)
    # Process the LLM output and create agents
    name_to_id = {}
    agents_to_add = []
    for agent_def in agent_definitions:
        agent_id = agent_network.get_next_agent_id()
        agent = Agent(
            agent_id=agent_id,
            name=agent_def['agent'].replace(' ', '_'),
            role=agent_def['role'],
            instructions=agent_def['instructions'],
            parent_id=None  # Will set parent_id later
        )
        name_to_id[agent.name] = agent_id
        agents_to_add.append((agent, agent_def.get('parent_id')))

    # Second pass to set parent_ids
    for agent, parent_name in agents_to_add:
        if parent_name and parent_name in name_to_id:
            agent.parent_id = name_to_id[parent_name]
        else:
            agent.parent_id = None
        agent_network.add_agent(agent)

    return redirect(url_for('manage_agents'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
