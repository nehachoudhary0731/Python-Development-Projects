from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import speech_recognition as sr
import pyttsx3
import requests
import threading
import time
import os
import json
import uuid
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'voice-assistant-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

CORS(app)

# API Keys
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

class AdvancedTTS:
    def __init__(self):
        self.tts_queue = []
        self.currently_speaking = False
        self.engine = None
        self.init_engine()
        
    def init_engine(self):
        """Initialize TTS engine with fallbacks"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  
            else:
                self.engine.setProperty('voice', voices[0].id)
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def speak(self, text, priority=False):
        """Add text to speech queue"""
        if priority:
            self.tts_queue.insert(0, text)  
        else:
            self.tts_queue.append(text)
        
        if not self.currently_speaking:
            self.process_queue()
    
    def process_queue(self):
        """Process the TTS queue"""
        if not self.tts_queue or self.currently_speaking:
            return
            
        self.currently_speaking = True
        thread = threading.Thread(target=self._process_queue_thread)
        thread.daemon = True
        thread.start()
    
    def _process_queue_thread(self):
        """Thread for processing TTS queue"""
        while self.tts_queue:
            try:
                text = self.tts_queue.pop(0)
                self._speak_sync(text)
                time.sleep(0.5)  
            except IndexError:
                break
        self.currently_speaking = False
    
    def _speak_sync(self, text):
        """Synchronous speech with new engine instance"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.error(f"TTS error: {e}")

tts_system = AdvancedTTS()

class AdvancedVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.reminders = []
        self.conversation_history = []
        self.user_preferences = {
            'location': 'New York',
            'news_categories': ['technology', 'general'],
            'speech_rate': 180
        }
        self.setup_reminder_scheduler()
    
    def setup_reminder_scheduler(self):
        """Setup background thread for checking reminders"""
        def check_reminders():
            while True:
                now = datetime.now()
                reminders_to_remove = []
                
                for i, reminder in enumerate(self.reminders):
                    if reminder['time'] <= now:
                        message = f"Reminder: {reminder['message']}"
                        tts_system.speak(message, priority=True)
                        reminders_to_remove.append(i)
                
                for i in sorted(reminders_to_remove, reverse=True):
                    self.reminders.pop(i)
                
                time.sleep(30)  
        
        reminder_thread = threading.Thread(target=check_reminders)
        reminder_thread.daemon = True
        reminder_thread.start()
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        tts_system.speak(text)
        return {"status": "success", "message": text}
    
    @lru_cache(maxsize=100)
    def get_weather(self, location=None):
        """Get weather information with caching"""
        if not OPENWEATHER_API_KEY:
            return "Weather service is not configured. Please add OpenWeather API key."
        
        location = location or self.user_preferences['location']
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                return f"In {location}, it's {temp}°C with {description}. Humidity is {humidity}%."
            else:
                return f"Could not get weather for {location}. Please try again later."
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return "Sorry, I'm having trouble accessing weather information."
    
    def get_news(self, category='general'):
        """Get news headlines"""
        if not NEWS_API_KEY:
            return "News service is not configured. Please add News API key."
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={category}&country=us&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data['articles']:
                articles = data['articles'][:3] 
                news_items = []
                for article in articles:
                    title = article['title']
                    source = article['source']['name']
                    news_items.append(f"{title} from {source}")
                
                return f"Here are the latest {category} news: {' '.join(news_items)}"
            else:
                return f"Could not fetch {category} news at the moment."
        except Exception as e:
            logger.error(f"News API error: {e}")
            return "Sorry, I'm having trouble accessing news."
    
    def set_reminder(self, message, minutes):
        """Set a reminder"""
        try:
            reminder_time = datetime.now() + timedelta(minutes=minutes)
            reminder = {
                'id': str(uuid.uuid4()),
                'message': message,
                'time': reminder_time,
                'set_time': datetime.now()
            }
            self.reminders.append(reminder)
            return f"I'll remind you about '{message}' in {minutes} minute{'s' if minutes != 1 else ''}."
        except Exception as e:
            logger.error(f"Reminder error: {e}")
            return "Sorry, I couldn't set that reminder."
    
    def get_time_date(self):
        """Get current time and date"""
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%A, %B %d, %Y")
        return f"The current time is {current_time} and today is {current_date}"
    
    def process_command(self, command, session_id):
        """Process voice commands with context"""
        command = command.lower()
        
        self.conversation_history.append({
            'session_id': session_id,
            'timestamp': datetime.now(),
            'command': command,
            'type': 'user'
        })
        
        response = self._determine_response(command)
        
        # Store assistant response
        self.conversation_history.append({
            'session_id': session_id,
            'timestamp': datetime.now(),
            'response': response,
            'type': 'assistant'
        })
        
        return response
    
    def _determine_response(self, command):
        """Determine appropriate response based on command"""
        # Greeting
        if any(word in command for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! How can I assist you today?"
        
        # Time and date
        elif any(word in command for word in ["time", "what time", "current time"]):
            return self.get_time_date()
        
        elif any(word in command for word in ["date", "what date", "today's date"]):
            return self.get_time_date()
        
        # Weather
        elif "weather" in command:
            location = self._extract_location(command)
            return self.get_weather(location)
        
        elif "news" in command:
            category = self._extract_news_category(command)
            return self.get_news(category)
        
        elif "remind" in command or "reminder" in command:
            return self._handle_reminder(command)
        
        elif "joke" in command:
            import pyjokes
            return pyjokes.get_joke()

        elif any(word in command for word in ["thank", "thanks", "appreciate"]):
            return "You're welcome! Is there anything else I can help with?"
    
        elif any(word in command for word in ["bye", "goodbye", "see you", "exit"]):
            return "Goodbye! Have a wonderful day!"
        
        elif "help" in command or "what can you do" in command:
            return self._get_help_message()
        
        else:
            return "I'm not sure how to help with that. You can ask me about time, weather, news, or to set reminders."
    
    def _extract_location(self, command):
        """Extract location from command"""
        locations = ["new york", "london", "paris", "tokyo", "mumbai", "delhi"]
        for location in locations:
            if location in command:
                return location
        return None
    
    def _extract_news_category(self, command):
        """Extract news category from command"""
        categories = {
            'technology': ['tech', 'technology', 'computer'],
            'sports': ['sports', 'game', 'football'],
            'business': ['business', 'economy', 'market'],
            'entertainment': ['entertainment', 'movie', 'celebrity']
        }
        
        for category, keywords in categories.items():
            if any(keyword in command for keyword in keywords):
                return category
        return 'general'
    
    def _handle_reminder(self, command):
        """Handle reminder commands"""
        try:
            if "in" in command and "minute" in command:
                parts = command.split()
                time_index = parts.index("in") + 1
                if time_index < len(parts):
                    minutes = int(parts[time_index])
                    if "to" in parts:
                        to_index = parts.index("to") + 1
                        message = " ".join(parts[to_index:])
                    else:
                        message = "something important"
                    
                    return self.set_reminder(message, minutes)
            return "Please specify when you'd like to be reminded, for example: 'remind me in 5 minutes to take a break'"
        except (ValueError, IndexError):
            return "I didn't understand the reminder format. Try: 'remind me in 10 minutes to call John'"
    
    def _get_help_message(self):
        """Get help message"""
        return """I can help you with:
• Telling current time and date
• Weather information for various cities
• Latest news updates
• Setting reminders
• Telling jokes
• And much more!

Try saying:
- "What's the weather in London?"
- "Tell me technology news"
- "Remind me in 10 minutes to take a break"
- "Tell me a joke"
- "What time is it?"""

# here we Initialize assistant
assistant = AdvancedVoiceAssistant()

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    result = assistant.text_to_speech(text)
    return jsonify(result)

@app.route('/process', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '')
    session_id = session.get('session_id', 'default')
    response = assistant.process_command(command, session_id)
    return jsonify({"response": response})

@app.route('/reminders', methods=['GET'])
def get_reminders():
    reminders = [
        {
            'message': reminder['message'],
            'time': reminder['time'].strftime('%Y-%m-%d %H:%M:%S'),
            'set_time': reminder['set_time'].strftime('%Y-%m-%d %H:%M:%S')
        }
        for reminder in assistant.reminders
    ]
    return jsonify({"reminders": reminders})

@app.route('/history', methods=['GET'])
def get_history():
    session_id = session.get('session_id', 'default')
    user_history = [
        item for item in assistant.conversation_history 
        if item['session_id'] == session_id
    ]
    return jsonify({"history": user_history})

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)