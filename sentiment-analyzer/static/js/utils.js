 // Utility functions for the sentiment analyzer

class SentimentUtils {
    static formatNumber(num, decimals = 2) {
        return Number(num).toFixed(decimals);
    }

    static getSentimentColor(score) {
        if (score >= 0.05) return '#27ae60'; // Positive - green
        if (score <= -0.05) return '#e74c3c'; // Negative - red
        return '#7f8c8d'; // Neutral - gray
    }

    static getSentimentIcon(sentiment) {
        switch(sentiment.toLowerCase()) {
            case 'positive': return 'fas fa-smile';
            case 'negative': return 'fas fa-frown';
            default: return 'fas fa-meh';
        }
    }

    static formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    static truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    static createChart(canvasId, config) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, config);
    }

    static calculateTextReadability(score) {
        if (score >= 90) return 'Very Easy';
        if (score >= 80) return 'Easy';
        if (score >= 70) return 'Fairly Easy';
        if (score >= 60) return 'Standard';
        if (score >= 50) return 'Fairly Difficult';
        if (score >= 30) return 'Difficult';
        return 'Very Difficult';
    }

    static getEmotionColor(emotion) {
        const colors = {
            'Happy': '#f39c12',
            'Angry': '#e74c3c',
            'Surprise': '#9b59b6',
            'Sad': '#3498db',
            'Fear': '#2c3e50'
        };
        return colors[emotion] || '#7f8c8d';
    }

    static getEmotionIcon(emotion) {
        const icons = {
            'Happy': 'fas fa-smile',
            'Angry': 'fas fa-angry',
            'Surprise': 'fas fa-surprise',
            'Sad': 'fas fa-sad-tear',
            'Fear': 'fas fa-flushed'
        };
        return icons[emotion] || 'fas fa-question';
    }
}

// DOM utility functions
class DOMUtils {
    static createElement(tag, classes = [], attributes = {}) {
        const element = document.createElement(tag);
        if (classes.length) {
            element.classList.add(...classes);
        }
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        return element;
    }

    static clearElement(element) {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    }

    static showElement(element) {
        element.classList.remove('hidden');
    }

    static hideElement(element) {
        element.classList.add('hidden');
    }

    static toggleElement(element) {
        element.classList.toggle('hidden');
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SentimentUtils, DOMUtils };
}