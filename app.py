# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_file
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

app = Flask(__name__)
socketio = SocketIO(app)
llm = LLM()
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
        report, conversation_log = run_simulation(task)
        # run_simulation(task)
        # conversation_log = agent_network.get_conversation_log()
        # report = agent_network.generate_final_report()
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
    instructions="""As a skilled business analyst and writer, generate a comprehensive report.
    Compile data and insights from all other agents, structure the report with clear sections and appropriate headings, introduction, body, and actionable conclusion. Ensure the report is clear, concise, and professional."""
)

def run_simulation(task):
    llm = LLM()  # Initialize your LLM client
    agent_network.execute(llm=llm, task=task)
    # Collect responses
    conversation_log = agent_network.collect_conversation_log()
    agents_data = agent_network.get_agents_responses()
    # Execute the report agent
    report_agent.execute(agents_data=agents_data, llm=llm)
    report = report_agent.response
    # Emit the new report to the frontend
    socketio.emit('update_report', {'report': report})
    return report, conversation_log

def extract_tagged_agents(message):
    # Use regex to find all words starting with '@'
    tagged_agents = re.findall(r'@(\w+)', message)
    return tagged_agents

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
    data = request.get_json()
    message = data.get('message', '')
    response = {'status': 'error'}

    tagged_agents = extract_tagged_agents(message)

    if tagged_agents:
        for agent_name in tagged_agents:
            agent = agent_network.find_agent_by_name(agent_name)
            if agent:
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
            else:
                response = {'status': 'error', 'message': f'Agent "{agent_name}" not found.'}
    else:
        response = {'status': 'error', 'message': 'No agent tagged.'}

    return jsonify(response)

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


if __name__ == '__main__':
    socketio.run(app, debug=True)
