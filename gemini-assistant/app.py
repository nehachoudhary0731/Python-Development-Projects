import os
import requests
import json
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# OpenRouter API configuration - FREE alternative to Gemini
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')  # Optional for better rates
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free models available on OpenRouter
FREE_MODELS = [
    "google/gemini-2.0-flash:free",
    "mistralai/mistral-7b-instruct:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-pro:free"
]

class RateLimiter:
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 2
        self.rate_limit_reset = 0
    
    def can_make_request(self):
        current_time = time.time()
        if current_time < self.rate_limit_reset:
            wait_time = self.rate_limit_reset - current_time
            return False, wait_time
        if current_time - self.last_request_time < self.min_interval:
            return False, self.min_interval
        return True, 0
    
    def record_request(self):
        self.last_request_time = time.time()
    
    def set_rate_limit(self, reset_time):
        self.rate_limit_reset = reset_time

rate_limiter = RateLimiter()

# Enhanced local knowledge base
FALLBACK_KNOWLEDGE = {
    'weather': "I can't access real-time weather data. For current weather, check Weather.com, AccuWeather, or your local weather service.",
    'price': "For current prices, I recommend checking Yahoo Finance, Google Finance, CoinMarketCap for crypto, or Bloomberg for stocks.",
    'news': "For the latest news, visit reputable sources like BBC News, Reuters, Associated Press, or CNN.",
    'bitcoin': "Bitcoin prices are highly volatile. Check real-time prices on CoinMarketCap, CoinGecko, Binance, or Coinbase.",
    'ethereum': "Ethereum prices change frequently. Monitor them on CoinMarketCap, CoinGecko, or major cryptocurrency exchanges.",
    'ai': "Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence, like learning, reasoning, and problem-solving.",
    'machine learning': "Machine Learning is a subset of AI that enables systems to learn patterns from data without explicit programming, using algorithms like neural networks.",
    'blockchain': "Blockchain is a decentralized digital ledger technology that records transactions securely and transparently across multiple computers.",
    'python': "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
    'flask': "Flask is a lightweight Python web framework that provides tools for building web applications quickly and with flexibility.",
    'api': "API (Application Programming Interface) is a set of rules that allows different software applications to communicate with each other.",
    'hello': "Hello! I'm an AI assistant. I can help with general knowledge questions and discussions on various topics.",
    'help': "I can answer questions about technology, science, programming, and general knowledge. Feel free to ask me anything!",
    'thank': "You're welcome! I'm happy to help. Is there anything else you'd like to know?",
    'how are you': "I'm functioning well, thank you for asking! I'm here to help you with information and answers to your questions."
}

def init_chat_history():
    if 'chat_history' not in session:
        session['chat_history'] = []
        session['chat_history'].append({
            "role": "system", 
            "content": "You are a helpful, knowledgeable AI assistant. Provide accurate information and be conversational. If you don't know something, be honest about it."
        })

def get_fallback_response(query):
    """Get intelligent fallback response based on query"""
    query_lower = query.lower()
    
    # Check for specific topics
    for keyword, response in FALLBACK_KNOWLEDGE.items():
        if keyword in query_lower:
            return response
    
    # If no specific match, generate a helpful response
    return f"I understand you're asking about '{query}'. This seems like an interesting topic! While I have general knowledge about many subjects, for the most current or specific information, you might want to consult specialized resources or databases. Would you like me to share what I know about related topics?"

def openrouter_chat(messages, model_name=None):
    """Call OpenRouter API for AI responses"""
    if not model_name:
        model_name = FREE_MODELS[0]  # Use first free model
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}" if OPENROUTER_API_KEY else ""
    }
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return None

@app.route('/')
def home():
    init_chat_history()
    status = {
        'ai_available': True,
        'service': 'OpenRouter (Free Models)',
        'rate_limited': time.time() < rate_limiter.rate_limit_reset,
        'models_available': len(FREE_MODELS)
    }
    return render_template('index.html', status=status)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Please enter a message'})
    
    init_chat_history()
    session['chat_history'].append({"role": "user", "content": user_message})
    
    # Check rate limiting
    can_request, wait_time = rate_limiter.can_make_request()
    if not can_request:
        fallback_response = f"Please wait {int(wait_time)} seconds before sending another message."
        session['chat_history'].append({"role": "model", "content": fallback_response})
        session.modified = True
        return jsonify({
            'response': fallback_response,
            'used_search': False,
            'rate_limited': True
        })
    
    rate_limiter.record_request()
    
    # Try OpenRouter API first
    try:
        # Prepare messages for API
        api_messages = []
        for msg in session['chat_history']:
            if msg['role'] == 'system':
                api_messages.append({"role": "system", "content": msg['content']})
            else:
                api_messages.append({"role": msg['role'], "content": msg['content']})
        
        # Try each free model until one works
        response_text = None
        for model_name in FREE_MODELS:
            response_text = openrouter_chat(api_messages, model_name)
            if response_text:
                break
        
        if response_text:
            session['chat_history'].append({"role": "model", "content": response_text})
            session.modified = True
            return jsonify({
                'response': response_text,
                'used_search': False,
                'rate_limited': False
            })
            
    except Exception as e:
        print(f"API error: {e}")
    
    # Fallback to local knowledge
    fallback_response = get_fallback_response(user_message)
    session['chat_history'].append({"role": "model", "content": fallback_response})
    session.modified = True
    
    return jsonify({
        'response': fallback_response,
        'used_search': False,
        'rate_limited': False
    })

@app.route('/clear', methods=['POST'])
def clear_chat():
    session['chat_history'] = []
    session['chat_history'].append({
        "role": "system", 
        "content": "You are a helpful, knowledgeable AI assistant. Provide accurate information and be conversational."
    })
    session.modified = True
    return jsonify({'status': 'Chat cleared'})

@app.route('/status')
def status_check():
    return jsonify({
        'service': 'OpenRouter with Free Models',
        'models_available': len(FREE_MODELS),
        'rate_limited': time.time() < rate_limiter.rate_limit_reset
    })

@app.route('/models')
def list_models():
    return jsonify({'free_models': FREE_MODELS})

if __name__ == '__main__':
    print("Starting AI Assistant with OpenRouter...")
    print(f"Available free models: {len(FREE_MODELS)}")
    for model in FREE_MODELS:
        print(f"  - {model}")
    app.run(debug=True, host='0.0.0.0', port=5000)