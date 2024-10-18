// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    function sendMessage() {
        const sendButton = document.getElementById('send-button');
        sendButton.disabled = true;
        sendButton.textContent = 'Sending...';
        console.log('sendMessage function called');
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        console.log('Message:', message);
        if (message === '') {
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            return;
        }
    
        // Display user's message
        const conversationLog = document.getElementById('conversation-log');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'user');
        messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
        conversationLog.appendChild(messageDiv);
        conversationLog.scrollTop = conversationLog.scrollHeight;
    
        // Send message to server
        fetch('/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && data.response) {
                const agentMessageDiv = document.createElement('div');
                agentMessageDiv.classList.add('message', 'ai', `agent-${data.agent_id}`);
                agentMessageDiv.innerHTML = `<strong>${data.agent_name}:</strong> ${data.response}`;
                conversationLog.appendChild(agentMessageDiv);
                conversationLog.scrollTop = conversationLog.scrollHeight;
            } else {
                throw new Error(data.message || 'An error occurred while sending the message.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        })
        .finally(() => {
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            input.value = '';
        });
    }

    // Attach event listeners
    document.getElementById('send-button').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Initialize Mermaid.js
    mermaid.initialize({ startOnLoad: true });

    // Handle Start Simulation button click
    $('#startSimulationBtn').click(function() {
        var simulationName = $('#simulationName').val().trim();
        if (simulationName === '') {
            showToast('Error', 'Please enter a simulation name.', 'danger');
        } else {
            $.post('/start_simulation', { name: simulationName }, function(response) {
                showToast('Simulation Started', `Simulation "${simulationName}" has begun.`, 'success');
                $('#simulationName').val('');
                // Update the tasks overview
                loadTasksOverview();
            });
        }
    });

    // Function to show toast notifications
    function showToast(title, message, variant) {
        toastr.options = {
            "positionClass": "toast-top-right",
            "timeOut": "5000",
        };
        if (variant === 'success') {
            toastr.success(message, title);
        } else if (variant === 'danger') {
            toastr.error(message, title);
        } else {
            toastr.info(message, title);
        }
    }

    // Define the functions and attach them to the window object
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
    window.saveConversation = saveConversation;

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
    window.saveReport = saveReport;

    // Load Agents Overview
    function loadAgentsOverview() {
        $.getJSON('/api/agents', function(data) {
            if (data.length > 0) {
                $('#agentsOverview').text(`${data.length} agents available.`);
            } else {
                $('#agentsOverview').text('No agents created yet.');
            }
        });
    }

    // Load Tasks Overview
    function loadTasksOverview() {
        $.getJSON('/api/tasks', function(data) {
            if (data.length > 0) {
                $('#tasksOverview').text(`${data.length} tasks in progress.`);
            } else {
                $('#tasksOverview').text('No active tasks.');
            }
        });
    }

    // Load Latest Reports
    function loadLatestReports() {
        $.getJSON('/api/reports/latest', function(data) {
            if (data && data.report_summary) {
                $('#latestReports').text(data.report_summary);
            } else {
                $('#latestReports').text('No reports generated yet.');
            }
        });
    }

    // Load System Status
    function loadSystemStatus() {
        // Implement any system checks if necessary
        $('#systemStatus').text('All systems operational.');
    }

    // Initial load
    loadAgentsOverview();
    loadTasksOverview();
    loadLatestReports();
    loadSystemStatus();

    // Refresh overviews periodically
    setInterval(function() {
        loadAgentsOverview();
        loadTasksOverview();
        loadLatestReports();
    }, 5000); // Refresh every 5 seconds

    // Draw Agent Network
    if ($('#agent-network').length) {
        drawAgentNetwork();
    }

    // Function to draw the agent network
    function drawAgentNetwork() {
        $.getJSON('/api/agents/network', function(data) {
            var nodes = new vis.DataSet(data.nodes);
            var edges = new vis.DataSet(data.edges);

            var container = document.getElementById('agent-network');
            var networkData = { nodes: nodes, edges: edges };
            var options = {
                nodes: {
                    shape: 'box',
                    color: '#6aa84f',
                    font: {
                        color: '#fff'
                    }
                },
                edges: {
                    arrows: 'to'
                },
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed'
                    }
                }
            };

            var network = new vis.Network(container, networkData, options);

            // Optional: Add event listeners for node interactions
            network.on('selectNode', function(params) {
                var agentId = params.nodes[0];
                // Fetch and display agent details
                $.getJSON('/api/agents/' + agentId, function(agent) {
                    // Populate and show a modal with agent details
                    $('#agentDetailsModal .modal-title').text(agent.name);
                    $('#agentDetailsModal #agentRole').text(agent.role);
                    $('#agentDetailsModal #agentInstructions').text(agent.instructions);
                    // Show the modal
                    $('#agentDetailsModal').modal('show');
                });
            });
        });
    }

    // Handle agent creation form submission
    $('#createAgentForm').submit(function(event) {
        event.preventDefault();
        var formData = {
            name: $('#agentName').val(),
            role: $('#agentRole').val(),
            instructions: $('#agentInstructions').val(),
            parent_id: $('#parent').val() || null
        };
        $.ajax({
            url: '/add_agent',
            type: 'POST',
            data: formData,
            success: function(response) {
                $('#createAgentModal').modal('hide');
                $('#createAgentForm')[0].reset();
                loadAgentsOverview();
                showToast('Success', 'Agent created successfully.', 'success');
            },
            error: function(error) {
                showToast('Error', 'Failed to create agent.', 'danger');
            }
        });
    });

    // Socket.IO events
    var socket = io;
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    socket.on('update', function(data) {
        // Handle real-time updates
    });
});