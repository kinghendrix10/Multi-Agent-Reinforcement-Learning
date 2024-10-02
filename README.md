# Multi-Agent Reinforcement Learning Simulator

This project is a multi-agent reinforcement learning simulator built using Flask for the backend and a combination of HTML, CSS, and JavaScript for the frontend. The simulator allows users to create, manage, and simulate interactions between multiple AI agents.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Running the App](#running-the-app)
- [Usage](#usage)
- [UI Elements](#ui-elements)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- Dashboard homepage with an overview and quick actions
- Card-based representation of agents and tasks
- Modal dialogs for creating/editing agents and executing tasks
- Tabs for conversation logs and report generation
- Real-time communication between agents and the frontend using Flask-SocketIO

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/kinghendrix10/Multi-Agent-Reinforcement-Learning.git
    cd Multi-Agent-Reinforcement-Learning
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory of the project.
    - Add the following environment variable:
        ```
        CEREBRAS_API_KEY=your_cerebras_api_key
        ```

## Running the App

1. Start the Flask application:
    ```bash
    flask run
    ```

2. Open your web browser and navigate to `http://localhost:5000` to access the simulator.

## Usage

### Dashboard

The dashboard provides an overview of the simulator and quick actions to start a new simulation.

### Agents

The agents section displays a card-based representation of all the agents. Each card shows the agent's role and tools. You can create, edit, and delete agents using the provided buttons.
The ReportAgent is created by default and can be edited but not deleted, as this is the agent that generates the final report.

### Tasks

The tasks section allows you to define and execute tasks for the agents. You can specify the task and the number of cycles for the simulation.

### Conversation Logs

The conversation logs tab displays the interactions between the agents during the simulation. You can tag any agent using "@" and the AgentName to request the agent to refine its output.

### Reports

The reports tab provides a detailed report of the simulation, including the contributions of each agent. You can save the report (Work in progress)

## UI Elements

### Modal Dialogs

Modal dialogs are used for creating and editing agents. The dialogs include fields for the agent's name, role, and instructions to guide it.

### Tabs

Tabs are used to switch between the conversation logs and the final report.

## API Endpoints

The simulator provides the following API endpoints:

- `GET /`: Renders the main page of the simulator.
- `POST /`: Starts a new simulation with the specified task and number of cycles.

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
