document.addEventListener('DOMContentLoaded', function() {
    const conversationLog = document.getElementById('conversation-log');
    if (conversationLog) {
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }
 
    const createAgentForm = document.getElementById('create-agent-form');
    const agentList = document.querySelector('.agents-grid');
 
    createAgentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const role = document.getElementById('agent-role').value.trim();
        const tools = document.getElementById('agent-tools').value.split(',').map(tool => tool.trim());
 
        const newAgent = document.createElement('div');
        newAgent.className = 'agent-card';
        newAgent.innerHTML = `
            <h3>${role}</h3>
            <p><strong>Role:</strong> ${role}</p>
            <p><strong>Tools:</strong> ${tools.join(', ')}</p>
            <button>Edit</button><button>Delete</button>`;
        agentList.appendChild(newAgent);
 
        // Clear form fields
        createAgentForm.reset();
    });
 
    window.editAgent = function(agentId) {
        alert(`Edit agent with ID ${agentId}`);
    };
 
    window.deleteAgent = function(agentId) {
        alert(`Delete agent with ID ${agentId}`);
    };
 });