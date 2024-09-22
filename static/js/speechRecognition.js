const outputDiv = document.getElementById("output");

if ("webkitSpeechRecognition" in window && "speechSynthesis" in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US"; // Set the language to English

    let recognizing = false;

    recognition.onstart = () => {
        recognizing = true;
        outputDiv.innerHTML = "Listening...";
        speak("Voice recognition activated. How can I assist you?");
    };

    recognition.onresult = (event) => {
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + " ";
                
                // Activate on "siri" and deactivate on "well done"
                if (finalTranscript.toLowerCase().includes("siri")) {
                    outputDiv.innerHTML += "<p>Voice recognition activated.</p>";
                } else if (finalTranscript.toLowerCase().includes("well done")) {
                    recognition.stop();
                    outputDiv.innerHTML += "<p>Voice recognition stopped.</p>";
                    speak("Voice recognition stopped. Thank you!");
                }
            }
        }

        outputDiv.innerHTML = finalTranscript;
    };

    recognition.onend = () => {
        recognizing = false;
        outputDiv.innerHTML += "<p>Stopped listening.</p>";
    };

    // Function to speak the message
    function speak(message) {
        const utterance = new SpeechSynthesisUtterance(message);
        speechSynthesis.speak(utterance);
    }

    // Start recognition automatically
    recognition.start();
} else {
    outputDiv.textContent = "Web Speech API not supported in this browser.";
}
