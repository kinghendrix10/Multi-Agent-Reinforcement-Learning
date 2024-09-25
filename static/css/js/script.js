// /static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const conversationLog = document.getElementById('conversation-log');
    if (conversationLog) {
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }
});
