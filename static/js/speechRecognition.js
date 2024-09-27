const outputDiv = document.getElementById("output");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");

if ("webkitSpeechRecognition" in window && "speechSynthesis" in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US"; // Set the language to English

    let recognizing = false;

    recognition.onstart = () => {
        recognizing = true;
        outputDiv.innerHTML = "Listening...";
        speak("Hello there! 😊 I'm Siri. How can I assist you today?");
    };

    recognition.onresult = (event) => {
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + " ";

                // Handle different commands and personalized greetings
                if (finalTranscript.toLowerCase().includes("siri")) {
                    outputDiv.innerHTML += "<p>Voice recognition activated.</p>";
                    speak("Hey! I'm Siri. Nice to be with you. What would you like to do next?");
                } else if (finalTranscript.toLowerCase().includes("hello")) {
                    speak("Hello! 😊 It's great to hear from you! How can I assist you today?");
                } else if (finalTranscript.toLowerCase().includes("good morning")) {
                    speak("Good morning! 🌅 I hope you're ready for a great day ahead.");
                } else if (finalTranscript.toLowerCase().includes("good evening")) {
                    speak("Good evening! 🌙 How was your day?");
                } else if (finalTranscript.toLowerCase().includes("thank you")) {
                    speak("You're welcome! 😇 I'm happy to help.");
                } else if (finalTranscript.toLowerCase().includes("well done")) {
                    recognition.stop();
                    outputDiv.innerHTML += "<p>Voice recognition stopped.</p>";
                    speak("Fantastic job! 🎉 Voice recognition stopped. Thank you for using my service!");
                } else if (finalTranscript.toLowerCase().includes("vote")) {
                    outputDiv.innerHTML += "<p>Voting system activated.</p>";
                    speak("You have activated the voting system.");
                } else {
                    // Search for buttons or links
                    executeCommand(finalTranscript.trim());
                }
            }
        }

        outputDiv.innerHTML = finalTranscript;
    };

    recognition.onend = () => {
        recognizing = false;
        outputDiv.innerHTML += "<p>Stopped listening.</p>";
        speak("Goodbye! Have a great day ahead! 😊");
    };

    // Function to speak the message
    function speak(message) {
        const utterance = new SpeechSynthesisUtterance(message);
        const selectedVoice = document.querySelector('input[name="voice"]:checked').value;
        const voices = speechSynthesis.getVoices();
        
        const voice = voices.find(voice => selectedVoice === "female" 
            ? voice.name.toLowerCase().includes("female")
            : voice.name.toLowerCase().includes("male")) || voices[0]; // Default to first available

        utterance.voice = voice;
        speechSynthesis.speak(utterance);
    }

    // Function to search and execute the command
    function executeCommand(command) {
        const elements = document.querySelectorAll("button, a"); // Select all buttons and links
        let found = false;

        elements.forEach(element => {
            if (element.textContent.toLowerCase() === command.toLowerCase()) {
                element.click(); // Simulate a click on the found element
                outputDiv.innerHTML += `<p>Clicked on: ${element.textContent}</p>`;
                speak(`Awesome! You've clicked on ${element.textContent}.`);

                // Provide additional feedback based on the element type or action
                if (element.tagName.toLowerCase() === 'button') {
                    speak(`You have successfully activated the ${element.textContent} action. Keep up the great work!`);
                } else if (element.tagName.toLowerCase() === 'a') {
                    speak(`Navigating to ${element.textContent}. I hope you enjoy your visit!`);
                }
                
                found = true;
            }
        });

        if (!found) {
            outputDiv.innerHTML += "<p>No matching button or link found.</p>";
            speak("Oops! I couldn't find any matching button or link. Please try again.");
        }
    }

    // Event listeners for starting and stopping recognition
    startBtn.addEventListener("click", () => {
        if (!recognizing) {
            recognition.start();
        }
    });

    stopBtn.addEventListener("click", () => {
        if (recognizing) {
            recognition.stop();
        }
    });

} else {
    outputDiv.textContent = "Web Speech API not supported in this browser.";
}
