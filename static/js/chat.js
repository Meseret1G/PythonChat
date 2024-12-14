const id = JSON.parse(document.getElementById('json-username').textContent);
const message_username = JSON.parse(document.getElementById('json-message-username').textContent);

const socket = new WebSocket('ws://' + window.location.host + '/ws/' + id + '/');

socket.binaryType = 'arraybuffer'; 
socket.onopen = function (event) {
    console.log("Connection established.");
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log("Received message:", data);

    // Create a new row for the incoming message
    let messageHTML = document.createElement('tr');
    const fileLink = data.file
        ? `<a href="${data.file}" target="_blank">${data.file.split('/').pop()}</a>`
        : '';
    const messageText = data.message ? data.message : 'No message content.';

    if (data.username === message_username) {
        messageHTML.innerHTML = `
            <td></td>
            <td class="text-right">
                <p class="message-sent">${messageText}</p>
                ${fileLink}
                <small class="timestamp">
                    ${data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </small>
            </td>`;
    } else {
        messageHTML.innerHTML = `
            <td class="text-left">
                <p class="message-received">${messageText}</p>
                ${fileLink}
                <small class="timestamp">
                    ${data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </small>
            </td>
            <td></td>`;
    }

    const chatBody = document.querySelector('#chat-body');
    chatBody.appendChild(messageHTML);
    chatBody.scrollTop = chatBody.scrollHeight; 
};

socket.onerror = function (event) {
    console.error("WebSocket error observed:", event);
};

socket.onclose = function (event) {
    console.log(`Connection closed: Code ${event.code}, Reason: ${event.reason}`);
};

document.querySelector('#chat-message-submit').onclick = function (event) {
    event.preventDefault();

    const messageInput = document.querySelector('#message_input');
    const fileInput = document.querySelector('#file_input');
    const message = messageInput.value.trim();

    if (!message && fileInput.files.length === 0) {
        return; 
    }

    const data = { message: message, username: message_username };

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];

        const formData = new FormData();
        formData.append('file', file);

        const fileReader = new FileReader();
        fileReader.onloadend = function () {
            const blobUrl = URL.createObjectURL(file);
            data.file = blobUrl; 
            socket.send(JSON.stringify(data));
            fileInput.value = ''; 
        };
        fileReader.readAsArrayBuffer(file); 
    } else {
        socket.send(JSON.stringify(data)); 
    }
 
    messageInput.value = ''; 
};