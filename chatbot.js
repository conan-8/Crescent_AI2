const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbot = document.querySelector(".chatbot");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector("#send-btn");
const chatbox = document.querySelector(".chatbox");

let userMessage = null;
let chatHistory = []; // Store conversation history
// The address of your local Python server
const API_URL = "https://w633xqhv-5000.use.devtunnels.ms/enrollment-chat";

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
                message: userMessage,
                history: chatHistory // Send history to server
            })
        });

        const data = await response.json();

        // Handle Rate Limit specifically
        if (response.status === 429) {
            throw new Error("You have sent too many messages recently. Please wait a minute before trying again.");
        }

        if (!response.ok) throw new Error(data.error || "Server Error");

        // Update the "Thinking..." text with the real answer
        // Helper to format text: escape HTML, parse markdown, linkify URLs, handle newlines
        const formatMessage = (text) => {
            // 1. Escape HTML to prevent XSS (must happen first)
            let safeText = text.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");

            // 2. Parse markdown - block level elements (headers, lists)
            const lines = safeText.split('\n');
            const processedLines = [];
            let inUnorderedList = false;
            let inOrderedList = false;

            for (let i = 0; i < lines.length; i++) {
                let line = lines[i];

                // Check for headers (## text) - convert to h3 as specified
                const headerMatch = line.match(/^(#{1,6})\s+(.+)$/);
                if (headerMatch) {
                    if (inUnorderedList) { processedLines.push('</ul>'); inUnorderedList = false; }
                    if (inOrderedList) { processedLines.push('</ol>'); inOrderedList = false; }
                    processedLines.push(`<h3>${headerMatch[2]}</h3>`);
                    continue;
                }

                // Check for unordered list items (- item or * item at start of line)
                const unorderedMatch = line.match(/^[-*]\s+(.+)$/);
                if (unorderedMatch) {
                    if (inOrderedList) { processedLines.push('</ol>'); inOrderedList = false; }
                    if (!inUnorderedList) { processedLines.push('<ul>'); inUnorderedList = true; }
                    processedLines.push(`<li>${unorderedMatch[1]}</li>`);
                    continue;
                }

                // Check for ordered list items (1. item, 2. item, etc.)
                const orderedMatch = line.match(/^\d+\.\s+(.+)$/);
                if (orderedMatch) {
                    if (inUnorderedList) { processedLines.push('</ul>'); inUnorderedList = false; }
                    if (!inOrderedList) { processedLines.push('<ol>'); inOrderedList = true; }
                    processedLines.push(`<li>${orderedMatch[1]}</li>`);
                    continue;
                }

                // Regular line - close any open lists
                if (inUnorderedList) { processedLines.push('</ul>'); inUnorderedList = false; }
                if (inOrderedList) { processedLines.push('</ol>'); inOrderedList = false; }
                processedLines.push(line);
            }

            // Close any remaining open lists
            if (inUnorderedList) processedLines.push('</ul>');
            if (inOrderedList) processedLines.push('</ol>');

            safeText = processedLines.join('\n');

            // 3. Parse markdown - inline elements
            // Bold (**text**) - must be parsed before italics
            safeText = safeText.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            // Italics (*text*) - single asterisks around text
            safeText = safeText.replace(/\*([^*\n]+?)\*/g, '<em>$1</em>');

            // 4. Linkify URLs (after markdown to avoid conflicts)
            safeText = safeText.replace(
                /(https?:\/\/[^\s<]+)/g,
                '<a href="$1" target="_blank" style="color: #00401A; text-decoration: underline;">$1</a>'
            );

            // 5. Handle newlines
            safeText = safeText.replace(/\n/g, "<br>");
            // Clean up <br> after/before block elements
            safeText = safeText.replace(/<\/h3><br>/g, '</h3>');
            safeText = safeText.replace(/<\/li><br>/g, '</li>');
            safeText = safeText.replace(/<\/ul><br>/g, '</ul>');
            safeText = safeText.replace(/<\/ol><br>/g, '</ol>');
            safeText = safeText.replace(/<ul><br>/g, '<ul>');
            safeText = safeText.replace(/<ol><br>/g, '<ol>');

            return safeText;
        };

        messageElement.innerHTML = formatMessage(data.response);

        // Add AI response to history
        chatHistory.push({ role: "model", content: data.response });

    } catch (error) {
        // Handle errors
        // If it's our custom rate limit error (or other server error msg), show that.
        // Otherwise, show generic connection error.
        if (error.message && (error.message.includes("429") || error.message.includes("Server Error"))) {
            messageElement.textContent = error.message;
        } else {
            messageElement.textContent = "Oops! I couldn't connect to the server. Make sure 'python server.py' is running.";
        }
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

    // Add user message to history
    chatHistory.push({ role: "user", content: userMessage });

    // Clear the input area and reset send button
    chatInput.value = "";
    sendChatBtn.classList.remove("active");

    // Display "Thinking..." message while we wait
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Call the real API
    generateResponse(incomingChatLi);
}

// Toggle send button active state based on textarea content
chatInput.addEventListener("input", () => {
    if (chatInput.value.trim()) {
        sendChatBtn.classList.add("active");
    } else {
        sendChatBtn.classList.remove("active");
    }
});

// Handle "Enter" key press
chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleChat();
    }
});

// Event Listeners
sendChatBtn.addEventListener("click", handleChat);
chatbotToggler.addEventListener("click", () => {
    const isShowing = document.body.classList.toggle("show-chatbot");
    // Notify parent window of toggle
    window.parent.postMessage({ type: "toggle", showing: isShowing }, "*");
});

// --- Resizing Logic ---

// 1. Create and inject the resize handle
const resizeHandle = document.createElement("div");
resizeHandle.classList.add("resize-handle");
chatbot.appendChild(resizeHandle);

// 2. Variables to track dragging
let isResizing = false;
let startX, startY, startWidth, startHeight;

// 3. Mouse Down Event
resizeHandle.addEventListener("mousedown", (e) => {
    e.preventDefault(); // Prevent text selection
    isResizing = true;
    startX = e.clientX;
    startY = e.clientY;
    startWidth = parseInt(document.defaultView.getComputedStyle(chatbot).width, 10);
    startHeight = parseInt(document.defaultView.getComputedStyle(chatbot).height, 10);

    // Disable transition during resize for smooth dragging
    chatbot.style.transition = 'none';

    document.addEventListener("mousemove", doDrag);
    document.addEventListener("mouseup", stopDrag);
});

// 4. Mouse Move Event (The actual resizing)
const doDrag = (e) => {
    if (!isResizing) return;

    // Calculate the new dimensions
    // Since we are dragging the top-left corner:
    // Moving left (negative dx) increases width
    // Moving up (negative dy) increases height
    const dx = startX - e.clientX;
    const dy = startY - e.clientY;

    const newWidth = startWidth + dx;
    const newHeight = startHeight + dy;

    // Apply new dimensions with minimum limits
    if (newWidth > 300) { // Min width
        chatbot.style.width = `${newWidth}px`;
    }
    if (newHeight > 400) { // Min height
        chatbot.style.height = `${newHeight}px`;
    }

    // Notify parent to resize the iframe
    window.parent.postMessage({
        type: "resize",
        width: chatbot.style.width,
        height: chatbot.style.height
    }, "*");
};

// 5. Mouse Up Event (Stop resizing)
const stopDrag = () => {
    isResizing = false;
    // Re-enable transition (optional, might want to keep it off if user resizes often)
    chatbot.style.transition = 'all 0.1s ease';

    document.removeEventListener("mousemove", doDrag);
    document.removeEventListener("mouseup", stopDrag);
};