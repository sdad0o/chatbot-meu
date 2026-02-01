document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatForm');
    const input = document.getElementById('userInput');
    const messagesDiv = document.getElementById('messages');
    const sendBtn = document.getElementById('sendBtn');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');

    // Suggestion Chips
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.textContent;
            input.value = text;
            form.dispatchEvent(new Event('submit'));
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        // Add User Message
        addMessage(message, 'user');
        input.value = '';
        sendBtn.disabled = true;

        // Show Loading
        const loadingId = addLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove Loading
            removeMessage(loadingId);

            if (data.error) {
                addMessage('Sorry, something went wrong: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        } catch (err) {
            removeMessage(loadingId);
            addMessage('Error: Could not connect to the server.', 'bot');
            console.error(err);
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    });

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        let content = text.replace(/\n/g, '<br>');
        
        msgDiv.innerHTML = `
            <div class="message-content">${content}</div>
        `;
        messagesDiv.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv.id = 'msg-' + Date.now();
    }

    function addLoading() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot';
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="message-content">
                <div class="loading-dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `;
        messagesDiv.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
});
