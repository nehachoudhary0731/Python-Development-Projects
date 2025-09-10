 // Main JavaScript functionality for sentiment analysis

class SentimentAnalyzerUI {
    constructor() {
        this.charts = {};
        this.currentResult = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Additional event listeners can be added here
        console.log('Sentiment Analyzer UI initialized');
    }

    displayAnalysisResults(data) {
        this.currentResult = data;
        const resultsContainer = document.getElementById('results');
        DOMUtils.clearElement(resultsContainer);
        
        this.createSentimentOverview(data);
        this.createDetailedAnalysis(data);
        this.createEmotionAnalysis(data);
        this.createTextStatistics(data);
        this.createKeywordAnalysis(data);
    }

    createSentimentOverview(data) {
        const resultsContainer = document.getElementById('results');
        const overviewCard = DOMUtils.createElement('div', ['sentiment-card']);
        
        const sentiment = data.basic_analysis.sentiment;
        const polarity = data.basic_analysis.polarity;
        
        overviewCard.innerHTML = `
            <div class="sentiment-header">
                <h3><i class="fas fa-chart-pie"></i> Sentiment Overview</h3>
                <span class="sentiment-badge badge-${sentiment.toLowerCase()}">
                    <i class="${SentimentUtils.getSentimentIcon(sentiment)}"></i>
                    ${sentiment}
                </span>
            </div>
            
            <div class="chart-grid">
                <div class="chart-wrapper">
                    <h4 class="chart-title">Sentiment Distribution</h4>
                    <div class="chart-container">
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-wrapper">
                    <h4 class="chart-title">Polarity Meter</h4>
                    <div class="sentiment-meter">
                        <div class="sentiment-indicator" style="left: ${((polarity + 1) / 2) * 100}%"></div>
                    </div>
                    <div class="meter-labels">
                        <span>Negative (-1.0)</span>
                        <span>Neutral (0.0)</span>
                        <span>Positive (+1.0)</span>
                    </div>
                    
                    <div class="progress-container">
                        <div class="progress-label">
                            <span>Polarity Score</span>
                            <span>${SentimentUtils.formatNumber(polarity)}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill progress-${sentiment.toLowerCase()}" 
                                 style="width: ${Math.abs(polarity) * 100}%"></div>
                        </div>
                    </div>
                    
                    <div class="progress-container">
                        <div class="progress-label">
                            <span>Subjectivity</span>
                            <span>${SentimentUtils.formatNumber(data.basic_analysis.subjectivity)}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill progress-neutral" 
                                 style="width: ${data.basic_analysis.subjectivity * 100}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(overviewCard);
        
        // Create sentiment chart
        setTimeout(() => {
            this.createSentimentChart(data.vader_analysis);
        }, 100);
    }

    createSentimentChart(vaderData) {
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        
        this.charts.sentiment = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [vaderData.positive, vaderData.negative, vaderData.neutral],
                    backgroundColor: [
                        '#27ae60', // Positive - green
                        '#e74c3c', // Negative - red
                        '#7f8c8d'  // Neutral - gray
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${(context.raw * 100).toFixed(1)}%`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    createDetailedAnalysis(data) {
        const resultsContainer = document.getElementById('results');
        const analysisCard = DOMUtils.createElement('div', ['sentiment-card']);
        
        analysisCard.innerHTML = `
            <div class="sentiment-header">
                <h3><i class="fas fa-microscope"></i> Detailed Analysis</h3>
            </div>
            
            <div class="chart-grid">
                <div class="chart-wrapper">
                    <h4 class="chart-title">TextBlob vs VADER Comparison</h4>
                    <div class="chart-container">
                        <canvas id="comparisonChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-wrapper">
                    <h4 class="chart-title">Analysis Scores</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(data.basic_analysis.polarity)}</div>
                            <div class="stat-label">TextBlob Polarity</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(data.vader_analysis.compound)}</div>
                            <div class="stat-label">VADER Compound</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(data.basic_analysis.subjectivity)}</div>
                            <div class="stat-label">Subjectivity</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(data.basic_analysis.confidence)}</div>
                            <div class="stat-label">Confidence</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(analysisCard);
        
        // Create comparison chart
        setTimeout(() => {
            this.createComparisonChart(data);
        }, 100);
    }

    createComparisonChart(data) {
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        
        this.charts.comparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['TextBlob', 'VADER'],
                datasets: [
                    {
                        label: 'Polarity Score',
                        data: [data.basic_analysis.polarity, data.vader_analysis.compound],
                        backgroundColor: '#4a6fa5',
                        borderColor: '#4a6fa5',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        min: -1,
                        max: 1,
                        ticks: {
                            stepSize: 0.5
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    createEmotionAnalysis(data) {
        const resultsContainer = document.getElementById('results');
        const emotionCard = DOMUtils.createElement('div', ['sentiment-card']);
        
        let emotionHTML = '';
        Object.entries(data.emotion_analysis).forEach(([emotion, score]) => {
            const percentage = (score * 100).toFixed(1);
            emotionHTML += `
                <div class="emotion-item emotion-${emotion.toLowerCase()}">
                    <i class="${SentimentUtils.getEmotionIcon(emotion)}"></i>
                    <div class="emotion-score">${percentage}%</div>
                    <div class="emotion-label">${emotion}</div>
                </div>
            `;
        });
        
        emotionCard.innerHTML = `
            <div class="sentiment-header">
                <h3><i class="fas fa-heart"></i> Emotion Analysis</h3>
            </div>
            
            <div class="emotion-grid">
                ${emotionHTML}
            </div>
            
            <div class="chart-container">
                <canvas id="emotionChart"></canvas>
            </div>
        `;
        
        resultsContainer.appendChild(emotionCard);
        
        // Create emotion chart
        setTimeout(() => {
            this.createEmotionChart(data.emotion_analysis);
        }, 100);
    }

    createEmotionChart(emotions) {
        const ctx = document.getElementById('emotionChart').getContext('2d');
        
        this.charts.emotion = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(emotions),
                datasets: [{
                    label: 'Emotion Intensity',
                    data: Object.values(emotions).map(val => val * 100),
                    backgroundColor: 'rgba(74, 111, 165, 0.2)',
                    borderColor: 'rgba(74, 111, 165, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(74, 111, 165, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(74, 111, 165, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    createTextStatistics(data) {
        const resultsContainer = document.getElementById('results');
        const statsCard = DOMUtils.createElement('div', ['sentiment-card']);
        
        const stats = data.text_statistics;
        const readability = data.readability_scores;
        
        statsCard.innerHTML = `
            <div class="sentiment-header">
                <h3><i class="fas fa-chart-bar"></i> Text Statistics</h3>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">${stats.word_count}</div>
                    <div class="stat-label">Words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.sentence_count}</div>
                    <div class="stat-label">Sentences</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.unique_words}</div>
                    <div class="stat-label">Unique Words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${SentimentUtils.formatNumber(stats.vocabulary_richness * 100)}%</div>
                    <div class="stat-label">Vocabulary Richness</div>
                </div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-wrapper">
                    <h4 class="chart-title">Readability Analysis</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${readability.flesch_reading_ease}</div>
                            <div class="stat-label">Flesch Score</div>
                            <small>${SentimentUtils.calculateTextReadability(readability.flesch_reading_ease)}</small>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${readability.flesch_kincaid_grade}</div>
                            <div class="stat-label">Grade Level</div>
                            <small>Approximate school grade</small>
                        </div>
                    </div>
                </div>
                
                <div class="chart-wrapper">
                    <h4 class="chart-title">Word Analysis</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(stats.avg_word_length)}</div>
                            <div class="stat-label">Avg Word Length</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${SentimentUtils.formatNumber(stats.avg_sentence_length)}</div>
                            <div class="stat-label">Avg Sentence Length</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(statsCard);
    }

    createKeywordAnalysis(data) {
        const resultsContainer = document.getElementById('results');
        const keywordCard = DOMUtils.createElement('div', ['sentiment-card']);
        
        let keywordHTML = '';
        data.keywords.forEach(([word, score]) => {
            const percentage = (score * 100).toFixed(1);
            keywordHTML += `<span class="keyword">${word} (${percentage}%)</span>`;
        });
        
        keywordCard.innerHTML = `
            <div class="sentiment-header">
                <h3><i class="fas fa-key"></i> Keyword Analysis</h3>
            </div>
            
            <div class="keywords-container">
                <p>Top keywords extracted from your text:</p>
                <div class="keyword-cloud">
                    ${keywordHTML}
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="keywordChart"></canvas>
            </div>
        `;
        
        resultsContainer.appendChild(keywordCard);
        
        // Create keyword chart
        setTimeout(() => {
            this.createKeywordChart(data.keywords);
        }, 100);
    }

    createKeywordChart(keywords) {
        const ctx = document.getElementById('keywordChart').getContext('2d');
        
        const labels = keywords.map(([word]) => word);
        const data = keywords.map(([_, score]) => score * 100);
        
        this.charts.keyword = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Importance Score (%)',
                    data: data,
                    backgroundColor: '#6e9cd2',
                    borderColor: '#4a6fa5',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Importance (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Keywords'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.sentimentUI = new SentimentAnalyzerUI();
    
    // Make display function available globally
    window.displayAnalysisResults = function(data) {
        window.sentimentUI.displayAnalysisResults(data);
    };
});