class VoiceAssistant {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.audioContext = null;
        this.analyser = null;
        this.visualizer = document.getElementById('visualizer');
        this.ctx = this.visualizer.getContext('2d');
        this.animationId = null;
        
        this.initializeSpeechRecognition();
        this.setupEventListeners();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.updateUI('listening', 'Listening...');
                this.startVisualization();
            };

            this.recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');

                if (event.results[0].isFinal) {
                    this.processCommand(transcript);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.addMessage('Assistant', 'Sorry, I didn\'t catch that. Please try again.');
                this.stopListening();
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
        } else {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
        }
    }

    setupEventListeners() {
        const listenBtn = document.getElementById('listenBtn');
        const stopBtn = document.getElementById('stopBtn');

        listenBtn.addEventListener('click', () => this.startListening());
        stopBtn.addEventListener('click', () => this.stopListening());
    }

    startListening() {
        if (this.recognition && !this.isListening) {
            this.isListening = true;
            document.getElementById('listenBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            this.recognition.start();
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.isListening = false;
            this.recognition.stop();
            document.getElementById('listenBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            this.updateUI('ready', 'Ready');
            this.stopVisualization();
        }
    }

    updateUI(state, message) {
        const status = document.getElementById('status');
        const avatar = document.querySelector('.assistant-avatar');
        
        status.textContent = message;
        avatar.classList.remove('listening', 'ready');
        avatar.classList.add(state);
    }

    addMessage(sender, text) {
        const conversation = document.getElementById('conversation');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase()}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        conversation.appendChild(messageDiv);
        conversation.scrollTop = conversation.scrollHeight;

        // If it's an assistant message, also speak it
        if (sender === 'Assistant') {
            this.speak(text);
        }
    }

    async processCommand(command) {
        this.addMessage('You', command);
        
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            const data = await response.json();
            this.addMessage('Assistant', data.response);
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Assistant', 'Sorry, I encountered an error processing your request.');
        }
        
        this.stopListening();
    }

    async speak(text) {
        try {
            await fetch('/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
        } catch (error) {
            console.error('Error with TTS:', error);
        }
    }

    startVisualization() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
        }

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                const source = this.audioContext.createMediaStreamSource(stream);
                source.connect(this.analyser);
                this.visualize();
            })
            .catch(err => {
                console.error('Error accessing microphone:', err);
            });
    }

    stopVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.ctx.clearRect(0, 0, this.visualizer.width, this.visualizer.height);
    }

    visualize() {
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            this.animationId = requestAnimationFrame(draw);
            this.analyser.getByteFrequencyData(dataArray);

            this.ctx.clearRect(0, 0, this.visualizer.width, this.visualizer.height);
            this.ctx.fillStyle = '#f8f9fa';
            this.ctx.fillRect(0, 0, this.visualizer.width, this.visualizer.height);

            const barWidth = (this.visualizer.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                this.ctx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
                this.ctx.fillRect(x, this.visualizer.height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }
        };

        draw();
    }
}

// Initialize the voice assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceAssistant();
});