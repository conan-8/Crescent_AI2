const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbot = document.querySelector(".chatbot");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");

let userMessage = null;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span>🤖</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message
    if(!userMessage) return;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);
    
    // Clear the input area
    chatInput.value = "";

    // Display "Thinking..." message after a short delay
    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // SIMULATION: For now, just reply with a dummy message after 1 second
        setTimeout(() => {
            incomingChatLi.querySelector("p").textContent = "I am the Crescent AI Prototype. I see you said: " + userMessage;
        }, 1000);

    }, 600);
}

// Handle "Enter" key press
chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window width is greater than 800px
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

// Event Listeners
sendChatBtn.addEventListener("click", handleChat);
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));