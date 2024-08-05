document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');

    chatForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(chatForm);

        // 사용자 입력 추가
        const userInput = document.getElementById('user-input').value;
        if (userInput) {
            chatBox.innerHTML += `<div class="user-message">${userInput}</div>`;
        }

        // 서버에 데이터 전송 및 응답 받기
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            // 챗봇 응답 추가
            if (data.response) {
                chatBox.innerHTML += `<div class="bot-message">${data.response}</div>`;
                if (data.image) {
                    chatBox.innerHTML += `<div class="bot-message"><img src="data:image/jpeg;base64,${data.image}" alt="Uploaded Image" style="max-width: 100%; height: auto;"></div>`;
                }
            } else if (data.error) {
                chatBox.innerHTML += `<div class="bot-message">Error: ${data.error}</div>`;
            }
        } catch (error) {
            console.error('Error:', error);
        }

        // 폼 리셋
        chatForm.reset();
        chatBox.scrollTop = chatBox.scrollHeight;
    });
});
