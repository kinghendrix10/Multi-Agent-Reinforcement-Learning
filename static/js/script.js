// static/js/script.js

function saveConversation() {
    const conversationLog = document.getElementById('conversation-log').innerText;
    fetch('/save_conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_log: conversationLog })
    })
    .then(response => response.json())
    .then(data => {
        alert('Conversation log saved successfully.');
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function saveReport() {
    const report = document.querySelector('pre').innerText;
    fetch('/save_report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report: report })
    })
    .then(response => response.json())
    .then(data => {
        alert('Report saved successfully.');
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message === '') return;

    // Display the user's message in the chat
    const conversationLog = document.getElementById('conversation-log');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'user');
    messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
    conversationLog.appendChild(messageDiv);
    conversationLog.scrollTop = conversationLog.scrollHeight;

    // Send the message to the server
    fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Display the agent's response
        if (data.response) {
            const agentMessageDiv = document.createElement('div');
            agentMessageDiv.classList.add('message', 'ai', `agent-${data.agent_id}`);
            agentMessageDiv.innerHTML = `<strong>${data.agent_name}:</strong> ${data.response}`;
            conversationLog.appendChild(agentMessageDiv);
            conversationLog.scrollTop = conversationLog.scrollHeight;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Clear the input
    input.value = '';
}
