document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearChatButton = document.getElementById('clear-chat');
    const connectionStatus = document.getElementById('connection-status');
    const messageCount = document.getElementById('message-count');
    
    let messageCounter = 0;
    
    // Focus input on load
    userInput.focus();
    
    // Update connection status
    connectionStatus.textContent = 'Connected';
    
    // Example chip click handler
    document.querySelectorAll('.example-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            userInput.value = chip.textContent;
            userInput.focus();
        });
    });
    
    // Update message count
    function updateMessageCount() {
        messageCounter++;
        messageCount.textContent = `Messages: ${messageCounter}`;
    }
    
    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat(message, 'user');
        updateMessageCount();
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.error) {
                addMessageToChat('Error: ' + data.error, 'bot');
            } else {
                addMessageToChat(data.response, 'bot', data.used_search);
            }
            
            // Update connection status if rate limited
            if (data.rate_limited) {
                connectionStatus.style.color = '#dc3545';
                connectionStatus.textContent = 'Rate Limited';
                userInput.disabled = true;
                sendButton.disabled = true;
                
                // Re-enable after a while
                setTimeout(() => {
                    userInput.disabled = false;
                    sendButton.disabled = false;
                    connectionStatus.style.color = '#28a745';
                    connectionStatus.textContent = 'Connected';
                }, 30000);
            }
        })
        .catch(error => {
            removeTypingIndicator();
            addMessageToChat('Error connecting to the server. Please try again.', 'bot');
            console.error('Error:', error);
            
            connectionStatus.style.color = '#dc3545';
            connectionStatus.textContent = 'Disconnected';
        });
    }
    
    // Add message to chat
    function addMessageToChat(message, sender, usedSearch = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        const icon = document.createElement('i');
        icon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        avatarDiv.appendChild(icon);
        
        const messageContentDiv = document.createElement('div');
        messageContentDiv.className = 'message-content';
        
        const messageText = document.createElement('p');
        messageText.textContent = message;
        messageContentDiv.appendChild(messageText);
        
        if (sender === 'bot' && usedSearch) {
            const searchIndicator = document.createElement('div');
            searchIndicator.className = 'search-indicator';
            searchIndicator.innerHTML = '<i class="fas fa-search"></i> Used real-time data';
            messageContentDiv.appendChild(searchIndicator);
        }
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(messageContentDiv);
        
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message bot-message';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-robot';
        avatarDiv.appendChild(icon);
        
        const messageContentDiv = document.createElement('div');
        messageContentDiv.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span style="margin-left: 10px; color: #666;">Thinking...</span>
        `;
        
        messageContentDiv.appendChild(typingIndicator);
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(messageContentDiv);
        
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Clear chat
    function clearChat() {
        fetch('/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(() => {
            // Clear the chat UI but keep the initial bot message
            const messages = chatHistory.querySelectorAll('.message');
            for (let i = 1; i < messages.length; i++) {
                messages[i].remove();
            }
            messageCounter = 0;
            messageCount.textContent = 'Messages: 0';
        })
        .catch(error => {
            console.error('Error clearing chat:', error);
        });
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !userInput.disabled) {
            sendMessage();
        }
    });
    
    clearChatButton.addEventListener('click', clearChat);
    
    // Check server status periodically
    setInterval(() => {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                if (data.rate_limited) {
                    connectionStatus.style.color = '#ffc107';
                    connectionStatus.textContent = 'Rate Limited';
                } else {
                    connectionStatus.style.color = '#28a745';
                    connectionStatus.textContent = 'Connected';
                }
            })
            .catch(() => {
                connectionStatus.style.color = '#dc3545';
                connectionStatus.textContent = 'Disconnected';
            });
    }, 30000);
});