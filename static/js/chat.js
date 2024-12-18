const id = JSON.parse(document.getElementById('json-username').textContent);
const message_username = JSON.parse(document.getElementById('json-message-username').textContent);

const socket = new WebSocket('ws://' + window.location.host + '/ws/' + id + '/');

socket.binaryType = 'arraybuffer'; 
socket.onopen = function (event) {
    console.log("Connection established.");
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    // Check if there's a message or a file, and render accordingly
    let messageHTML = document.createElement('tr');

    const fileLink = data.file
        ? `<p class="file-link"><a href="${data.file}" target="_blank">${data.file.split('/').pop()}</a></p>`
        : '';

    const messageText = data.message ? data.message : null;

    // Render message if there's a message, or just the file if no message
    if (data.username === message_username) {
        messageHTML.innerHTML = `
            <td></td>
            <td class="text-right">
                ${messageText ? `<p class="message-sent">${messageText}</p>` : ''}
                ${fileLink ? `<p class="file-sent">${fileLink}</p>` : ''}
                <small class="timestamp">
                    ${data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </small>
            </td>`;
    } else {
        messageHTML.innerHTML = `
            <td class="text-left">
                ${messageText ? `<p class="message-received">${messageText}</p>` : ''}
                ${fileLink ? `<p class="file-received">${fileLink}</p>` : ''}
                <small class="timestamp">
                    ${data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </small>
            </td>
            <td></td>`;
    }

    const chatBody = document.querySelector('#chat-body');
    chatBody.appendChild(messageHTML);
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom
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

        const fileReader = new FileReader();
        fileReader.onloadend = function () {
            const base64File = fileReader.result; // Base64-encoded file
            console.log("Base64 File Sent:", base64File); // Log base64 file data to console
        
            data.file = base64File; // Attach the base64 string
            socket.send(JSON.stringify(data)); // Send the data
            fileInput.value = ''; // Clear the file input
        };
        fileReader.readAsDataURL(file);
    } else {
        socket.send(JSON.stringify(data)); 
    }

    messageInput.value = ''; 
};
