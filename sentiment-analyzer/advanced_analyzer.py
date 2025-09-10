from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
import string
import pandas as pd
import numpy as np
from datetime import datetime

class AdvancedSentimentAnalyzer:
    def __init__(self):
        self._download_nltk_data()
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        self.emotion_lexicon = {
            'happy': ['happy', 'joy', 'excited', 'pleased', 'delighted', 'wonderful', 'great', 'awesome'],
            'angry': ['angry', 'mad', 'furious', 'outraged', 'annoyed', 'irritated', 'frustrated'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'wow', 'unexpected'],
            'sad': ['sad', 'unhappy', 'depressed', 'miserable', 'sorrow', 'grief', 'heartbroken'],
            'fear': ['afraid', 'scared', 'fearful', 'terrified', 'anxious', 'worried', 'nervous']
        }
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        required_data = ['punkt', 'stopwords', 'vader_lexicon', 'averaged_perceptron_tagger']
        for dataset in required_data:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
            except LookupError:
                nltk.download(dataset)
    
    def analyze_text(self, text, advanced=True):
        """Perform comprehensive sentiment analysis"""
        if not text or len(text.strip()) == 0:
            return self._create_empty_result()
        
        cleaned_text = self._clean_text(text)
        
        blob = TextBlob(cleaned_text)
        polarity = round(blob.sentiment.polarity, 3)
        subjectivity = round(blob.sentiment.subjectivity, 3)
        
        vader_scores = self.sia.polarity_scores(cleaned_text)
        
        sentiment_label = self._get_sentiment_label(polarity)
        vader_label = self._get_sentiment_label(vader_scores['compound'])
        
        result = {
            'text': text,
            'cleaned_text': cleaned_text,
            'timestamp': datetime.now().isoformat(),
            'basic_analysis': {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment': sentiment_label,
                'confidence': abs(polarity)  
            },
            'vader_analysis': {
                'compound': round(vader_scores['compound'], 3),
                'positive': round(vader_scores['pos'], 3),
                'negative': round(vader_scores['neg'], 3),
                'neutral': round(vader_scores['neu'], 3),
                'sentiment': vader_label
            }
        }
        
        if advanced:
            result.update(self._advanced_analysis(cleaned_text))
        
        return result
    
    def _advanced_analysis(self, text):
        """Perform advanced text analysis"""
        emotions = self._analyze_emotions(text)
        
        stats = self._get_text_statistics(text)
        
        keywords = self._extract_keywords(text)
        
        readability = self._calculate_readability(text)
        
        return {
            'emotion_analysis': emotions,
            'text_statistics': stats,
            'keywords': keywords[:10],  
            'readability_scores': readability
        }
    
    def _analyze_emotions(self, text):
        """Custom emotion analysis to replace text2emotion"""
        words = word_tokenize(text.lower())
        emotion_scores = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
        
        for word in words:
            for emotion, keywords in self.emotion_lexicon.items():
                if word in keywords:
                    emotion_scores[emotion] += 1
        
        total_emotion_words = sum(emotion_scores.values())
        if total_emotion_words > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = round(emotion_scores[emotion] / total_emotion_words, 3)
        
        return {
            'Happy': emotion_scores['happy'],
            'Angry': emotion_scores['angry'],
            'Surprise': emotion_scores['surprise'],
            'Sad': emotion_scores['sad'],
            'Fear': emotion_scores['fear']
        }
    
    def _clean_text(self, text):
        """Clean and preprocess text"""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.lower()
    
    def _get_sentiment_label(self, score):
        """Convert score to sentiment label"""
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _get_text_statistics(self, text):
        """Calculate text statistics"""
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        meaningful_words = [word for word in words if word.lower() not in self.stop_words and len(word) > 2]
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'unique_words': len(set(words)),
            'avg_word_length': round(np.mean([len(word) for word in words]), 2) if words else 0,
            'avg_sentence_length': round(len(words) / len(sentences), 2) if sentences else 0,
            'stopword_count': len(words) - len(meaningful_words),
            'vocabulary_richness': round(len(set(words)) / len(words), 3) if words else 0
        }
    
    def _extract_keywords(self, text, n=10):
        """Extract top keywords using TF-IDF like approach"""
        words = [word for word in word_tokenize(text) 
                if word.lower() not in self.stop_words and len(word) > 2]
        
        word_freq = Counter(words)
        total_words = len(words)
        
        keywords = [(word, count/total_words) for word, count in word_freq.most_common(n*2)]
        
        keywords = [kw for kw in keywords if kw[1] < 0.1][:n]
        
        return keywords
    
    def _calculate_readability(self, text):
        """Calculate readability scores"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        if not sentences or not words:
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0}
        
        total_sentences = len(sentences)
        total_words = len(words)
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        flesch_ease = 206.835 - 1.015 * (total_words/total_sentences) - 84.6 * (total_syllables/total_words)
        
        flesch_grade = 0.39 * (total_words/total_sentences) + 11.8 * (total_syllables/total_words) - 15.59
        
        return {
            'flesch_reading_ease': round(flesch_ease, 2),
            'flesch_kincaid_grade': round(flesch_grade, 2)
        }
    
    def _count_syllables(self, word):
        """Approximate syllable count for a word"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count
    
    def _create_empty_result(self):
        """Create empty result structure"""
        return {
            'text': '',
            'cleaned_text': '',
            'timestamp': datetime.now().isoformat(),
            'basic_analysis': {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'Neutral',
                'confidence': 0
            },
            'vader_analysis': {
                'compound': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'sentiment': 'Neutral'
            },
            'emotion_analysis': {'Happy': 0, 'Angry': 0, 'Surprise': 0, 'Sad': 0, 'Fear': 0},
            'text_statistics': {
                'word_count': 0,
                'sentence_count': 0,
                'unique_words': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0,
                'stopword_count': 0,
                'vocabulary_richness': 0
            },
            'keywords': [],
            'readability_scores': {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0}
        }
analyzer = AdvancedSentimentAnalyzer()