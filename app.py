from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from lead_analyzer import get_composite_lead_score
# from waitress import serve
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

import nltk
import os

nltk.data.path.append(os.getenv("NLTK_DATA", "nltk_data"))
nltk.download('vader_lexicon')

# Initialize Flask app
app = Flask(__name__)

# Add route for frontend
@app.route('/', methods=['GET'])
def index():
    """Serve the main frontend page"""
    return render_template('index.html')

@app.route('/api/analyze-lead', methods=['POST'])
def analyze_lead():
    """
    API endpoint to analyze a lead message and return a structured JSON response.
    
    Expected JSON payload:
    {
        "message": "The lead message to analyze"
    }
    
    Returns:
    JSON response with lead analysis results
    """
    
    # Check if request has JSON data
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 400
    
    # Get the message from the request
    data = request.get_json()
    app.logger.info(f"Received data: {data}")
    
    # Validate that message is provided
    if 'message' not in data or not data['message']:
        return jsonify({
            "error": "Message field is required"
        }), 400
    
    # Get the message
    message = data['message']
    
    try:
        # Call the lead analysis function from lead_analyzer.py
        result = get_composite_lead_score(message)
        
        # Return the result as JSON
        return jsonify(result)
    
    except Exception as e:
        # Handle any errors
        app.logger.error(f"Error processing lead message: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "lead-score-ai-agent"
    })

# if __name__ == '__main__':
# #     # Get port from environment variable or use default
# #     port = int(os.environ.get('PORT', 5000))
    
#     # Run the app
#     # app.run(host='0.0.0.0', port=port, debug=False) 
#     serve(app, host="0.0.0.0", port=8000)