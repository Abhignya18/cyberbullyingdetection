async function sendData() {
    let textInput = document.getElementById("text");
    let fileInput = document.getElementById("file");
    let chat = document.getElementById("chat-box");

    let text = textInput.value.trim();
    let file = fileInput.files[0];

    if (!text && !file) {
        alert("Enter text or upload file");
        return;
    }

    // ✅ Show user message FIRST
    if (text) {
        chat.innerHTML += `<div class="msg user">${text}</div>`;
    } else {
        chat.innerHTML += `<div class="msg user">📎 Screenshot uploaded</div>`;
    }

    chat.scrollTop = chat.scrollHeight;

    let formData = new FormData();
    if (text) formData.append("text", text);
    if (file) formData.append("file", file);

    try {
        let res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        let data = await res.json();

        console.log("API RESPONSE:", data); // 🔥 IMPORTANT

        // ✅ FIX: Ensure values exist
        let result = data.result ? data.result : "No result";
        let confidence = data.confidence !== undefined ? data.confidence : 0;

        chat.innerHTML += `
            <div class="msg bot">
                ${result} (${confidence}%)
            </div>
        `;

    } catch (error) {
        console.log("ERROR:", error);
        chat.innerHTML += `<div class="msg bot">❌ Error</div>`;
    }

    // ✅ Clear AFTER response
    textInput.value = "";
    fileInput.value = "";

    chat.scrollTop = chat.scrollHeight;
}