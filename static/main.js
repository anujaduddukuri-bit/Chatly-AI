// static/main.js
(function () {
  const chatWindow = document.getElementById("chat-window");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("msg");
  const sendBtn = document.getElementById("sendBtn");

  // Build WS URL based on current origin
  const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProtocol}://${window.location.host}/ws/chat`;
  const socket = new WebSocket(wsUrl);

  socket.addEventListener("open", () => {
    addBot("Connected! 👋 Say hi to start.");
  });

  socket.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.type === "bot_message" && payload.text) {
        addBot(payload.text);
      }
    } catch (e) {
      // Fallback for non-JSON messages
      addBot(String(event.data));
    }
  });

  socket.addEventListener("close", () => {
    addBot("Disconnected. Refresh to reconnect.");
  });

  socket.addEventListener("error", () => {
    addBot("Connection error. Check server logs.");
  });

  function addUser(text) {
    const el = document.createElement("div");
    el.className = "msg user";
    el.textContent = text;
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function addBot(text) {
    const el = document.createElement("div");
    el.className = "msg bot";
    el.textContent = text;
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addUser(text);

    const payload = { type: "user_message", text };
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    } else {
      addBot("Unable to send — socket is not open.");
    }

    input.value = "";
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });
})();