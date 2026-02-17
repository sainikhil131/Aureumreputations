// Aureum Chatbot JavaScript

class AureumChatbot {
    constructor() {
        this.isOpen = false;
        this.conversationHistory = [];
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
        this.showWelcomeMessage();
    }

    createChatWidget() {
        // Create chat button
        const chatButton = document.createElement('button');
        chatButton.className = 'chat-widget-button';
        chatButton.id = 'chatWidgetButton';
        chatButton.innerHTML = '<i class="fas fa-comments"></i>';
        chatButton.setAttribute('aria-label', 'Open chat');
        document.body.appendChild(chatButton);

        // Create chat container
        const chatContainer = document.createElement('div');
        chatContainer.className = 'chat-widget-container';
        chatContainer.id = 'chatWidgetContainer';
        chatContainer.innerHTML = `
            <div class="chat-header">
                <div class="chat-header-content">
                    <div class="chat-avatar">✨</div>
                    <div class="chat-header-text">
                        <h3>Aureum Assistant</h3>
                        <p>Your reputation consultant</p>
                    </div>
                </div>
                <button class="chat-close-btn" id="chatCloseBtn" aria-label="Close chat">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chat-messages" id="chatMessages">
                <!-- Messages will be added here -->
            </div>
            <div class="typing-indicator" id="typingIndicator">
                <div class="message-avatar" style="background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%); color: white;">✨</div>
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
            <div class="chat-input-area">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="chatInput" 
                    placeholder="Type your message..."
                    autocomplete="off"
                />
                <button class="chat-send-btn" id="chatSendBtn" aria-label="Send message">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
        document.body.appendChild(chatContainer);
    }

    attachEventListeners() {
        const chatButton = document.getElementById('chatWidgetButton');
        const chatCloseBtn = document.getElementById('chatCloseBtn');
        const chatSendBtn = document.getElementById('chatSendBtn');
        const chatInput = document.getElementById('chatInput');

        chatButton.addEventListener('click', () => this.toggleChat());
        chatCloseBtn.addEventListener('click', () => this.toggleChat());
        chatSendBtn.addEventListener('click', () => this.sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const chatContainer = document.getElementById('chatWidgetContainer');
        const chatButton = document.getElementById('chatWidgetButton');

        if (this.isOpen) {
            chatContainer.classList.add('active');
            chatButton.classList.add('active');
            document.getElementById('chatInput').focus();
        } else {
            chatContainer.classList.remove('active');
            chatButton.classList.remove('active');
        }
    }

    showWelcomeMessage() {
        const welcomeMsg = {
            type: 'bot',
            text: "Hello! How can I help you today?"
        };
        this.addMessage(welcomeMsg);
    }

    addMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.type === 'bot' ? '✨' : '👤';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message.text;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.add('active');
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.remove('active');
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const sendBtn = document.getElementById('chatSendBtn');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to UI
        this.addMessage({ type: 'user', text: message });
        this.conversationHistory.push({ role: 'user', message: message });

        // Clear input and disable button
        input.value = '';
        sendBtn.disabled = true;

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend (use APP_ROOT if available for subdirectory deployment)
            const appRoot = window.APP_ROOT || '';
            const response = await fetch(`${appRoot}/chatbot`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory
                })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            if (data.success) {
                // Add bot response
                this.addMessage({ type: 'bot', text: data.response });
                this.conversationHistory.push({ role: 'bot', message: data.response });
            } else {
                this.addMessage({ 
                    type: 'bot', 
                    text: "I apologize, but I'm experiencing technical difficulties. Please try again or contact us directly." 
                });
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTypingIndicator();
            this.addMessage({ 
                type: 'bot', 
                text: "I apologize, but I'm having trouble connecting. Please try again in a moment." 
            });
        } finally {
            // Re-enable send button
            sendBtn.disabled = false;
            input.focus();
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aureumChatbot = new AureumChatbot();
});

