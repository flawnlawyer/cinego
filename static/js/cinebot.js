// ================== CINEBOT CHAT WIDGET ==================

class CineBotWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.initWidget();
        this.loadChatHistory();
    }

    initWidget() {
        // Add widget HTML to page
        const widgetHTML = `
            <div class="cinebot-widget">
                <button class="cinebot-button" id="cinebot-toggle">
                    <i class="fas fa-robot"></i>
                    <span class="notification-dot" id="cinebot-notification"></span>
                </button>

                <div class="cinebot-window" id="cinebot-window">
                    <div class="cinebot-header">
                        <div class="cinebot-header-left">
                            <div class="cinebot-avatar">🤖</div>
                            <div class="cinebot-title">
                                <h3>CineBot</h3>
                                <p>Your movie companion</p>
                            </div>
                        </div>
                        <button class="cinebot-close" id="cinebot-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="watch-warning" id="watch-warning">
                        <i class="fas fa-clock"></i>
                        <span id="watch-warning-text"></span>
                    </div>

                    <div class="cinebot-messages" id="cinebot-messages">
                        <div class="chat-message">
                            <div class="message-avatar bot">🤖</div>
                            <div class="message-content bot">
                                <p>Hi! I'm CineBot, your personal movie guide! 🎬</p>
                                <p>Ask me to recommend movies, check your watch time, or just chat about films!</p>
                            </div>
                        </div>
                    </div>

                    <div class="cinebot-input-area">
                        <div class="cinebot-quick-actions">
                            <button class="quick-action-btn" data-message="Recommend an action movie">🎬 Action</button>
                            <button class="quick-action-btn" data-message="I feel happy">😊 Happy mood</button>
                            <button class="quick-action-btn" data-message="What should I watch?">💡 Surprise me</button>
                            <button class="quick-action-btn" data-message="How much have I watched today?">⏱️ Watch time</button>
                        </div>
                        <form class="cinebot-input-form" id="cinebot-form">
                            <input 
                                type="text" 
                                class="cinebot-input" 
                                id="cinebot-input" 
                                placeholder="Ask me anything..."
                                autocomplete="off"
                            >
                            <button type="submit" class="cinebot-send" id="cinebot-send">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);

        // Attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Toggle chat window
        document.getElementById('cinebot-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        document.getElementById('cinebot-close').addEventListener('click', () => {
            this.toggleChat();
        });

        // Handle form submission
        document.getElementById('cinebot-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                document.getElementById('cinebot-input').value = message;
                this.sendMessage();
            });
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('cinebot-window');
        
        if (this.isOpen) {
            window.classList.add('active');
            document.getElementById('cinebot-notification').style.display = 'none';
            document.getElementById('cinebot-input').focus();
        } else {
            window.classList.remove('active');
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/chat/history');
            const data = await response.json();
            
            if (data.success && data.history.length > 0) {
                const messagesContainer = document.getElementById('cinebot-messages');
                // Clear initial message
                messagesContainer.innerHTML = '';
                
                data.history.forEach(msg => {
                    this.displayMessage(msg.message, msg.is_bot, false);
                });
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    async sendMessage() {
        const input = document.getElementById('cinebot-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input
        input.value = '';

        // Display user message
        this.displayMessage(message, false);

        // Show typing indicator
        this.showTyping();

        try {
            // Send to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTyping();

            if (data.success) {
                // Display bot response
                this.displayMessage(data.response, true);

                // Show watch time warning if exists
                if (data.watch_warning) {
                    this.showWatchWarning(data.watch_warning);
                }
            } else {
                this.displayMessage("Oops! Something went wrong. Try again?", true);
            }

        } catch (error) {
            this.hideTyping();
            this.displayMessage("Sorry, I'm having connection issues. Please try again!", true);
            console.error('Chat error:', error);
        }
    }

    displayMessage(text, isBot, scroll = true) {
        const messagesContainer = document.getElementById('cinebot-messages');
        
        const messageHTML = `
            <div class="chat-message ${isBot ? 'bot' : 'user'}">
                <div class="message-avatar ${isBot ? 'bot' : 'user'}">
                    ${isBot ? '🤖' : '👤'}
                </div>
                <div class="message-content ${isBot ? 'bot' : 'user'}">
                    ${this.formatMessage(text)}
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);

        // Auto-scroll to bottom
        if (scroll) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    formatMessage(text) {
        // Convert markdown-style bold to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to <br>
        text = text.replace(/\n/g, '<br>');
        
        return `<p>${text}</p>`;
    }

    showTyping() {
        const messagesContainer = document.getElementById('cinebot-messages');
        
        const typingHTML = `
            <div class="chat-message bot typing-indicator">
                <div class="message-avatar bot">🤖</div>
                <div class="cinebot-typing active">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="text-muted" style="font-size: 0.8rem;">CineBot is thinking...</span>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showWatchWarning(message) {
        const warning = document.getElementById('watch-warning');
        const warningText = document.getElementById('watch-warning-text');
        
        warningText.textContent = message;
        warning.classList.add('active');

        // Auto-hide after 10 seconds
        setTimeout(() => {
            warning.classList.remove('active');
        }, 10000);
    }

    showNotification() {
        const notification = document.getElementById('cinebot-notification');
        if (!this.isOpen) {
            notification.style.display = 'block';
        }
    }
}

// Initialize CineBot when page loads
let cineBot;
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on logged-in pages
    if (document.querySelector('header nav')) {
        cineBot = new CineBotWidget();
        console.log('🤖 CineBot initialized and ready!');
    }
});

// ================== WATCH TIME TRACKING ==================

// Track watch time on video player page
if (window.location.pathname.startsWith('/watch/')) {
    let watchStartTime = Date.now();
    let movieId = parseInt(window.location.pathname.split('/').pop());

    // Update watch time every 2 minutes
    setInterval(async () => {
        const currentTime = Date.now();
        const minutesWatched = Math.floor((currentTime - watchStartTime) / 60000);

        if (minutesWatched > 0) {
            try {
                const response = await fetch('/update_watch_time', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        movie_id: movieId,
                        minutes: minutesWatched
                    })
                });

                const data = await response.json();
                
                if (data.success && data.warning) {
                    // Show warning in CineBot if it exists
                    if (window.cineBot) {
                        cineBot.showWatchWarning(data.warning);
                        cineBot.showNotification();
                    }
                }

                // Reset start time
                watchStartTime = currentTime;

            } catch (error) {
                console.error('Failed to update watch time:', error);
            }
        }
    }, 120000); // Every 2 minutes
}

console.log('🎬 CineBot AI system loaded!');
