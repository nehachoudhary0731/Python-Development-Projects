from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from advanced_analyzer import analyzer
from config import Config
from datetime import datetime, timedelta
import json
import uuid

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    text = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'result': json.loads(self.result),
            'timestamp': self.timestamp.isoformat()
        }

# Creating tables
with app.app_context():
    db.create_all()

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = Config.SESSION_TIMEOUT
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Please enter some text to analyze'}), 400
        
        if len(text) > Config.MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text too long. Maximum {Config.MAX_TEXT_LENGTH} characters allowed.'
            }), 400
        
        result = analyzer.analyze_text(text)
        
        history_entry = AnalysisHistory(
            session_id=session['session_id'],
            text=text,
            result=json.dumps(result)
        )
        db.session.add(history_entry)
        db.session.commit()
        
        old_entries = AnalysisHistory.query.filter(
            AnalysisHistory.session_id == session['session_id']
        ).order_by(AnalysisHistory.timestamp.desc()).offset(Config.MAX_HISTORY_ITEMS).all()
        
        for entry in old_entries:
            db.session.delete(entry)
        db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'An error occurred during analysis. Please try again.'}), 500

@app.route('/history')
def get_history():
    try:
        history = AnalysisHistory.query.filter(
            AnalysisHistory.session_id == session['session_id']
        ).order_by(AnalysisHistory.timestamp.desc()).limit(20).all()
        
        return jsonify({
            'history': [entry.to_dict() for entry in history]
        })
    
    except Exception as e:
        app.logger.error(f"History error: {str(e)}")
        return jsonify({'error': 'Could not retrieve history'}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    try:
        AnalysisHistory.query.filter(
            AnalysisHistory.session_id == session['session_id']
        ).delete()
        db.session.commit()
        return jsonify({'message': 'History cleared successfully'})
    
    except Exception as e:
        app.logger.error(f"Clear history error: {str(e)}")
        return jsonify({'error': 'Could not clear history'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)