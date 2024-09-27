// // static/js/main.js
// $(document).ready(function() {
//     // Initialize Socket.IO client
//     var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

//     // Load agents and tasks on page load
//     loadAgents();
//     loadTasks();

//     // Handle agent creation
//     $('#createAgentForm').submit(function(event) {
//         event.preventDefault();
//         var name = $('#agentName').val();
//         var role = $('#agentRole').val();
//         var tools = $('#agentTools').val().split(',').map(function(item) {
//             return item.trim();
//         });

//         $.ajax({
//             url: '/api/agents',
//             type: 'POST',
//             contentType: 'application/json',
//             data: JSON.stringify({ 'name': name, 'role': role, 'tools': tools }),
//             success: function(response) {
//                 $('#createAgentModal').modal('hide');
//                 $('#createAgentForm')[0].reset();
//                 loadAgents();
//             },
//             error: function(error) {
//                 alert('Error creating agent');
//             }
//         });
//     });

//     // Handle task creation
//     $('#createTaskForm').submit(function(event) {
//         event.preventDefault();
//         var task = $('#taskDescription').val();
//         var cycles = $('#taskCycles').val();

//         // Submit task via form post
//         $.ajax({
//             url: '/',
//             type: 'POST',
//             data: { 'task': task, 'cycles': cycles },
//             success: function(response) {
//                 $('#createTaskModal').modal('hide');
//                 $('#createTaskForm')[0].reset();
//                 loadTasks();
//             },
//             error: function(error) {
//                 alert('Error creating task');
//             }
//         });
//     });

//     // Socket.IO events
//     socket.on('connect', function() {
//         console.log('Connected to server');
//     });

//     socket.on('task_completed', function(data) {
//         // Display the report and conversation log
//         alert('Task completed');
//         loadConversations();
//     });

//     // Load agents
//     function loadAgents() {
//         $.ajax({
//             url: '/api/agents',
//             type: 'GET',
//             success: function(agents) {
//                 var agentsList = $('#agentsList');
//                 var agentsContainer = $('#agentsContainer');
//                 agentsList.empty();
//                 agentsContainer.empty();

//                 agents.forEach(function(agent) {
//                     var agentItem = $('<a href="#" class="list-group-item list-group-item-action"></a>').text(agent.name + ' (' + agent.role + ')');
//                     agentsList.append(agentItem);

//                     var agentCard = `
//                     <div class="col-md-4">
//                         <div class="card">
//                             <div class="card-header">
//                                 ${agent.name}
//                             </div>
//                             <div class="card-body">
//                                 <h5 class="card-title">${agent.role}</h5>
//                                 <p class="card-text">Tools: ${agent.tools.join(', ')}</p>
//                                 <button class="btn btn-sm btn-danger delete-agent" data-agent-id="${agent.id}">Delete</button>
//                             </div>
//                         </div>
//                     </div>`;
//                     agentsContainer.append(agentCard);
//                 });

//                 // Handle agent deletion
//                 $('.delete-agent').click(function() {
//                     var agentId = $(this).data('agent-id');
//                     $.ajax({
//                         url: '/api/agents/' + agentId,
//                         type: 'DELETE',
//                         success: function(response) {
//                             loadAgents();
//                         },
//                         error: function(error) {
//                             alert('Error deleting agent');
//                         }
//                     });
//                 });
//             },
//             error: function(error) {
//                 alert('Error loading agents');
//             }
//         });
//     }

//     // Load tasks
//     function loadTasks() {
//         // Since tasks are not stored persistently, this function can be expanded when tasks are stored.
//         // For now, we can display a placeholder.
//         var tasksList = $('#tasksList');
//         var tasksContainer = $('#tasksContainer');
//         tasksList.empty();
//         tasksContainer.empty();

//         var taskItem = $('<a href="#" class="list-group-item list-group-item-action"></a>').text('No tasks available');
//         tasksList.append(taskItem);
//     }

//     // Load conversation logs
//     function loadConversations() {
//         $.ajax({
//             url: '/api/conversations',
//             type: 'GET',
//             success: function(conversations) {
//                 var conversationLog = $('#conversationLog');
//                 conversationLog.empty();

//                 conversations.forEach(function(entry) {
//                     var logEntry = $('<p></p>').text(entry);
//                     conversationLog.append(logEntry);
//                 });
//             },
//             error: function(error) {
//                 alert('Error loading conversations');
//             }
//         });
//     }
// });


// /static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
   const socket = io.connect('http://' + document.domain + ':' + location.port);

   socket.on('connect', function() {
       socket.send('User connected');
   });

   socket.on('response', function(data) {
       console.log(data);
       // Update UI based on data received
   });

   const createAgentForm = document.getElementById('createAgentForm');
   createAgentForm.addEventListener('submit', function(e) {
       e.preventDefault();
       const name = document.getElementById('agentName').value.trim();
       const role = document.getElementById('agentRole').value.trim();
       const tools = document.getElementById('agentTools').value.split(',').map(tool => tool.trim());

       // Send new agent data to server
       fetch('/api/agents', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ name, role, tools })
       }).then(response => response.json()).then(data => {
           console.log(data);
           // Update UI with new agent
       });

       createAgentForm.reset();
   });
});
