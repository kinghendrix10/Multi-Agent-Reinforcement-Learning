document.addEventListener('DOMContentLoaded', function() {
    const conversationLog = document.getElementById('conversation-log');
    if (conversationLog) {
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }

    const createAgentForm = document.getElementById('create-agent-form');
    const agentList = document.querySelector('.agents-grid');

    createAgentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('agent-name').value.trim();
        const role = document.getElementById('agent-role').value.trim();
        const tools = document.getElementById('agent-tools').value.split(',').map(tool => tool.trim());

        const newAgent = document.createElement('div');
        newAgent.className = 'agent-card';
        newAgent.innerHTML = `
            <h3>${name}</h3>
            <p><strong>Role:</strong> ${role}</p>
            <p><strong>Tools:</strong> ${tools.join(', ')}</p>
            <button onclick="editAgent('${name}')">Edit</button>
            <button onclick="deleteAgent('${name}')">Delete</button>`;
        agentList.appendChild(newAgent);

        // Clear form fields
        createAgentForm.reset();
    });

    window.editAgent = function(agentName) {
        alert(`Edit agent: ${agentName}`);
    };

    window.deleteAgent = function(agentName) {
        alert(`Delete agent: ${agentName}`);
    };

    const ws = new WebSocket('ws://localhost:8765');
    ws.onopen = function() {
        console.log("Connected to WebSocket server");
    };

    ws.onmessage = function(event) {
        const message = event.data;
        const newMessage = document.createElement('p');
        newMessage.textContent = message;
        conversationLog.appendChild(newMessage);
        conversationLog.scrollTop = conversationLog.scrollHeight;
    };

    ws.onerror = function(error) {
        console.error("WebSocket error:", error);
    };

    ws.onclose = function() {
        console.log("WebSocket connection closed");
    };
});