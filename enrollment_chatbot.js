const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbot = document.querySelector(".chatbot");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector("#send-btn");
const chatbox = document.querySelector(".chatbox");
const closeBtn = document.querySelector(".close-btn");
const newChatBtn = document.querySelector(".new-chat-btn");

let userMessage = null;
let chatHistory = []; // Store conversation history
const welcomeScreen = document.getElementById('welcome-screen');

const showWelcome = () => {
    if (!welcomeScreen) return;
    welcomeScreen.classList.remove('hidden');
    welcomeScreen.classList.remove('fade-in');
    void welcomeScreen.offsetWidth; // force reflow to restart animation
    welcomeScreen.classList.add('fade-in');
};
// The address of your local Python server
const API_URL = "http://127.0.0.1:5000/enrollment-chat";

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = `<p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const startThinkingAnimation = (messageElement) => {
    messageElement.innerHTML = '<span class="thinking-animation"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>';
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
            // 0. Extract source line before processing to avoid regex conflicts
            let sourceBubbleHtml = '';
            const sourceMatch = text.match(/\n\nSource:\s+(https?:\/\/\S+)/);
            if (sourceMatch) {
                const rawUrl = sourceMatch[1];
                const domainMatch = rawUrl.match(/https?:\/\/(?:www\.)?([^\/\s?#]+)/);
                const displayName = domainMatch ? domainMatch[1] : 'Source';
                const safeUrl = rawUrl.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
                sourceBubbleHtml = `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" class="source-bubble"><svg width="9" height="9" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 2L2 10M10 2H5M10 2V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>${displayName}</a>`;
                text = text.replace(/\n\nSource:\s+https?:\/\/\S+/, '');
            }

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
                '<a href="$1" target="_blank" style="color: #006e4f; text-decoration: underline; max-width: 100%; display: inline-block; overflow: hidden; text-overflow: ellipsis; vertical-align: bottom; white-space: nowrap;">$1</a>'
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

            // Append source bubble if present
            if (sourceBubbleHtml) {
                safeText += '<div class="source-line">' + sourceBubbleHtml + '</div>';
            }

            return safeText;
        };

        messageElement.innerHTML = formatMessage(data.response);

        // Trigger top-to-bottom reveal animation on the response
        incomingChatLi.classList.remove("response-reveal");
        void incomingChatLi.offsetHeight; // force reflow to restart animation
        incomingChatLi.classList.add("response-reveal");

        // Add AI response to history
        chatHistory.push({ role: "model", content: data.response });

        // Enrollment banner is persistent — no need to append scheduler options here

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
        // No scroll — response stays below the visible area; user scrolls manually.
    }
}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message
    if (!userMessage) return;

    // Hide welcome screen and show chatbox on first message
    if (welcomeScreen && !welcomeScreen.classList.contains('hidden')) {
        welcomeScreen.classList.add('hidden');
        chatbox.style.display = '';
    }

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));

    // Clear the input area and reset send button
    chatInput.value = "";
    chatInput.style.height = "38px";
    sendChatBtn.classList.remove("active");

    // Enrollment banner is persistent — no cleanup generatedScheduler buttons here

    // Add user message to history
    chatHistory.push({ role: "user", content: userMessage });

    // Display animated thinking indicator while we wait
    const incomingChatLi = createChatLi("", "incoming");
    startThinkingAnimation(incomingChatLi.querySelector("p"));
    chatbox.appendChild(incomingChatLi);

    // Call the real API
    generateResponse(incomingChatLi);
}

// Toggle send button active state based on textarea content
chatInput.addEventListener("input", () => {
    // Adjust height dynamically based on content
    chatInput.style.height = "38px";
    let newHeight = chatInput.scrollHeight;
    if (newHeight > 180) newHeight = 180; // ensure max height is respected, but scroll kicks in
    chatInput.style.height = `${newHeight}px`;

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
    window.parent.postMessage({ type: "toggle", showing: isShowing }, "*");
    if (isShowing && welcomeScreen && !welcomeScreen.classList.contains('hidden')) {
        showWelcome();
    }
});

closeBtn.addEventListener("click", () => {
    document.body.classList.remove("show-chatbot");
    window.parent.postMessage({ type: "toggle", showing: false }, "*");
});

// New Chat button: clear conversation and restore welcome screen
newChatBtn.addEventListener("click", () => {
    chatbox.innerHTML = "";
    chatbox.style.display = 'none';
    showWelcome();
    chatHistory = [];
    chatInput.value = "";
    chatInput.style.height = "38px";
    sendChatBtn.classList.remove("active");
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
