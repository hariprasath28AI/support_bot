// ---------------------------------  ------------------------


document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const initialBotMessage = document.createElement("p");
    initialBotMessage.textContent = "Hello, how can I assist you?";
    initialBotMessage.className = "bot-message";
    chatBox.appendChild(initialBotMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
  
  function handleKeyPress(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  }
  
  function formatResponse(response) {
    // Bold text
    response = response.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  
    // Numbered list to bullet points
    response = response.replace(/(\d+)\.\s*(.*?)(?=\n|$)/g, "<li>$2</li>");
    if (response.includes("<li>")) {
      response = `<ul>${response}</ul>`;
    }
  
    return response;
  }
  
  function createCodeContainer(code) {
    const pre = document.createElement("pre");
    const codeElement = document.createElement("code");
    codeElement.textContent = code.trim();
  
    const copyButton = document.createElement("button");
    copyButton.textContent = "Copy";
    copyButton.className = "copy-button";
    copyButton.onclick = () => {
      navigator.clipboard.writeText(code.trim()).then(() => {
        copyButton.textContent = "Copied!";
        setTimeout(() => {
          copyButton.textContent = "Copy";
        }, 2000);
      });
    };
  
    pre.appendChild(codeElement);
    pre.appendChild(copyButton);
    return pre;
  }
  
  async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;
  
    const chatBox = document.getElementById("chat-box");
    const userMessage = document.createElement("p");
    userMessage.textContent = `${userInput}`;
    userMessage.className = "user-message";
    chatBox.appendChild(userMessage);
  
    try {
      const response = await fetch("http://0.0.0.0:8080/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userInput }),
      });
  
      const data = await response.json();
      const botMessage = document.createElement("div");
      botMessage.className = "bot-message";
  
      let formattedResponse = formatResponse(data.response);
  
      // Handle code blocks
      const codeRegex = /```([\s\S]*?)```/g;
      let match;
      while ((match = codeRegex.exec(formattedResponse)) !== null) {
        const codeContainer = createCodeContainer(match[1]);
        formattedResponse = formattedResponse.replace(match[0], codeContainer.outerHTML);
      }
  
      botMessage.innerHTML = formattedResponse;
  
      // Reattach event listeners to copy buttons
      botMessage.querySelectorAll('.copy-button').forEach(button => {
        button.onclick = () => {
          const code = button.previousElementSibling.textContent;
          navigator.clipboard.writeText(code).then(() => {
            button.textContent = "Copied!";
            setTimeout(() => {
              button.textContent = "Copy";
            }, 2000);
          });
        };
      });
  
      chatBox.appendChild(botMessage);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = document.createElement("p");
      errorMessage.textContent = `Bot: Sorry, there was an error processing your request.`;
      errorMessage.className = "bot-message";
      chatBox.appendChild(errorMessage);
    }
  
    document.getElementById("user-input").value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  