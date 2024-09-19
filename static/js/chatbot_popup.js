document.addEventListener('DOMContentLoaded', function () {
    const chatbotBtn = document.getElementById('chatbot-open-btn');
    const chatbotPopup = document.getElementById('chatbot-popup-container');
    const chatbotCloseBtn = document.getElementById('chatbot-close-btn');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    let isFirstOpen = true;

    if (chatbotBtn && chatbotPopup) {
        chatbotBtn.onclick = () => {
            if (chatbotPopup.style.display === 'block') {
                chatbotPopup.style.display = 'none';
            } else {
                chatbotPopup.style.display = 'block';

                if (isFirstOpen) {
                    chatbotMessages.innerHTML += `<div class="bot-message">hello, weather gpt free to ask!</div>`;
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                    isFirstOpen = false;
                }
            }
        };
    }

    if (chatbotCloseBtn) {
        chatbotCloseBtn.onclick = () => {
            chatbotPopup.style.display = 'none';
        };
    }

    if (chatbotForm) {
        chatbotForm.addEventListener('submit', function (e) {
            e.preventDefault();
    
            const userInput = chatbotInput.value;
    
            const userMessage = document.createElement('div');
            userMessage.classList.add('user-message');
            userMessage.classList.add('message-slide-in-right');
            userMessage.innerHTML = userInput;
            chatbotMessages.appendChild(userMessage);
    
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('typing-indicator');
            typingIndicator.innerText = 'Bot is typing...';
            chatbotMessages.appendChild(typingIndicator);
    
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    
            // Gửi văn bản tới server
            const formData = new FormData();
            formData.append('message', userInput);
    
            fetch('/chatbot', {
                method: 'POST',
                body: formData  // Gửi dữ liệu dưới dạng form-data
            })
            .then(response => response.json())
            .then(data => {
                typingIndicator.remove();
                const botMessage = document.createElement('div');
                botMessage.classList.add('bot-message');
                botMessage.classList.add('message-slide-in-left');
                botMessage.innerHTML = data.response;
                chatbotMessages.appendChild(botMessage);
    
                chatbotInput.value = '';
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                typingIndicator.remove();
            });
        });
    }
});
