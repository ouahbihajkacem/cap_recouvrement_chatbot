document.getElementById('chat-icon').addEventListener('click', function () {
    document.getElementById('chat-bubble').style.display = 'flex';
    document.getElementById('chat-icon').style.display = 'none';
});

document.getElementById('close-chat').addEventListener('click', function () {
    document.getElementById('chat-bubble').style.display = 'none';
    document.getElementById('chat-icon').style.display = 'block';
});

document.getElementById('send-button').addEventListener('click', function () {
    let userInput = document.getElementById('user-input').value;
    if (userInput.trim()) {
        addUserMessage(userInput);
        fetch('https://your-backend-url.onrender.com/api/chat', { // Remplacez par l'URL de votre backend Render
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput, first_name: "FirstName", last_name: "LastName" })
        })
        .then(response => response.json())
        .then(data => {
            addBotMessage(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

function addUserMessage(message) {
    let chatMessages = document.getElementById('chat-messages');
    let userMessageElement = document.createElement('div');
    userMessageElement.className = 'user-message';
    userMessageElement.textContent = message;
    chatMessages.appendChild(userMessageElement);
    document.getElementById('user-input').value = '';
}

function addBotMessage(message) {
    let chatMessages = document.getElementById('chat-messages');
    let botMessageElement = document.createElement('div');
    botMessageElement.className = 'bot-message';
    botMessageElement.textContent = message;
    chatMessages.appendChild(botMessageElement);
}
