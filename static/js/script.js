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
