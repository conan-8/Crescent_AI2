const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbot = document.querySelector(".chatbot");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");

let userMessage = null;
// The address of your local Python server
const API_URL = "http://127.0.0.1:5000/chat";

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span>🤖</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const generateResponse = async (incomingChatLi) => {
    const messageElement = incomingChatLi.querySelector("p");

    try {
        // Send POST request to your Python Server
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userMessage
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server Error");

        // Update the "Thinking..." text with the real answer
        // Helper to format text: escape HTML, linkify URLs, handle newlines
        const formatMessage = (text) => {
            // 1. Escape HTML to prevent XSS (basic)
            let safeText = text.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");

            // 2. Linkify URLs
            // Regex to find URLs (starting with http:// or https://)
            safeText = safeText.replace(
                /(https?:\/\/[^\s]+)/g,
                '<a href="$1" target="_blank" style="color: #00401A; text-decoration: underline;">$1</a>'
            );

            // 3. Handle newlines
            return safeText.replace(/\n/g, "<br>");
        };

        messageElement.innerHTML = formatMessage(data.response);

    } catch (error) {
        // Handle errors (like if the server isn't running)
        messageElement.textContent = "Oops! I couldn't connect to the server. Make sure 'python server.py' is running.";
        messageElement.style.color = "#cc0000";
    } finally {
        // Scroll to bottom to see the new message
        chatbox.scrollTo(0, chatbox.scrollHeight);
    }
}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message
    if (!userMessage) return;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Clear the input area
    chatInput.value = "";

    // Display "Thinking..." message while we wait
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Call the real API
    generateResponse(incomingChatLi);
}

// Handle "Enter" key press
chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window width is greater than 800px
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

// Event Listeners
sendChatBtn.addEventListener("click", handleChat);
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));