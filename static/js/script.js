document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const leadForm = document.getElementById('leadForm');
    const leadMessage = document.getElementById('leadMessage');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultSection = document.getElementById('resultSection');
    const sentimentScore = document.getElementById('sentimentScore');
    const aiScore = document.getElementById('aiScore');
    const compositeScore = document.getElementById('compositeScore');
    const justification = document.getElementById('justification');
    const jsonOutput = document.getElementById('jsonOutput');
    const exampleCards = document.querySelectorAll('.example-card');

    // Submit form handler
    leadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get the message
        const message = leadMessage.value.trim();
        
        if (!message) {
            alert('Please enter a lead message to analyze.');
            return;
        }
        
        // Show loading state
        setLoading(true);
        
        // Call the API
        analyzeLead(message);
    });

    // Handle example clicks
    exampleCards.forEach(card => {
        card.addEventListener('click', function() {
            const example = this.getAttribute('data-example');
            leadMessage.value = example;
            
            // Scroll to the form
            leadForm.scrollIntoView({ behavior: 'smooth' });
            
            // Focus the textarea
            setTimeout(() => {
                leadMessage.focus();
            }, 500);
        });
    });

    // Function to analyze lead
    function analyzeLead(message) {
        fetch('/api/analyze-lead', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('API request failed');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
            setLoading(false);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while analyzing the lead. Please try again.');
            setLoading(false);
        });
    }

    // Function to display results
    function displayResults(data) {
        // Show the results section
        resultSection.classList.add('active');
        
        // Populate sentiment score
        let sentimentLabel = data.sentiment.label;
        let sentimentClass = getSentimentClass(sentimentLabel);
        sentimentScore.textContent = sentimentLabel;
        sentimentScore.className = 'score-value ' + sentimentClass;
        
        // Populate AI score
        let aiScoreValue = data.ai_analysis.score;
        let aiScoreClass = getScoreClass(aiScoreValue);
        aiScore.textContent = aiScoreValue;
        aiScore.className = 'score-value ' + aiScoreClass;
        
        // Populate composite score
        let finalScoreValue = data.composite_score;
        let finalScoreClass = getScoreClass(finalScoreValue);
        compositeScore.textContent = finalScoreValue;
        compositeScore.className = 'score-value ' + finalScoreClass;
        
        // Populate justification
        justification.textContent = data.ai_analysis.justification;
        
        // Populate JSON output
        jsonOutput.textContent = JSON.stringify(data, null, 2);
        
        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Helper function to get sentiment class
    function getSentimentClass(sentiment) {
        sentiment = sentiment.toLowerCase();
        if (sentiment.includes('positive')) {
            return 'sentiment-positive';
        } else if (sentiment.includes('negative')) {
            return 'sentiment-negative';
        } else {
            return 'sentiment-neutral';
        }
    }

    // Helper function to get score class
    function getScoreClass(score) {
        if (score >= 70) {
            return 'score-high';
        } else if (score >= 40) {
            return 'score-medium';
        } else {
            return 'score-low';
        }
    }

    // Function to set loading state
    function setLoading(isLoading) {
        if (isLoading) {
            analyzeBtn.classList.add('loading');
            analyzeBtn.disabled = true;
        } else {
            analyzeBtn.classList.remove('loading');
            analyzeBtn.disabled = false;
        }
    }
}); 