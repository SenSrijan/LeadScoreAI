# Lead Score AI Agent

This application provides an AI-powered lead scoring system with a beautiful web interface.

## Features

- AI-based lead scoring using advanced language models
- Sentiment analysis of lead messages
- Beautiful, modern web interface
- RESTful API for integration with other systems
- Pre-built examples for quick testing

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

3. Run the Flask application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000/
   ```

## Project Structure

- `app.py` - Flask server that provides the API endpoints and serves the web interface
- `lead_analyzer.py` - Core lead scoring logic and AI analysis functionality
- `ChatOpenRouter.py` - Handles communication with the OpenRouter API
- `templates/index.html` - HTML structure for the web interface
- `static/css/style.css` - Styling for the web interface
- `static/js/script.js` - JavaScript for dynamic behavior on the frontend

## Web Interface

The application includes a sleek, modern web interface that allows you to:

- Enter lead messages for analysis
- View detailed scoring results with visual indicators
- See the sentiment analysis, AI analysis, and composite score
- Read the AI's justification for the scoring
- View the raw JSON response
- Try pre-built examples with a single click

## API Endpoints

### Analyze Lead

**Endpoint:** `/api/analyze-lead`

**Method:** POST

**Content-Type:** application/json

**Request Body:**
```json
{
  "message": "The lead message to analyze"
}
```

**Response:**
```json
{
  "message": "The lead message to analyze",
  "sentiment": {
    "label": "Positive",
    "compound_score": 0.6369
  },
  "ai_analysis": {
    "score": 75,
    "justification": "The lead shows strong interest and has requested specific information about pricing."
  },
  "composite_score": 72
}
```

### Health Check

**Endpoint:** `/api/health`

**Method:** GET

**Response:**
```json
{
  "status": "healthy",
  "service": "lead-score-ai-agent"
}
```

## Example Usage

### Using the Web Interface

1. Open your browser to `http://localhost:5000/`
2. Enter a lead message or click one of the example messages
3. Click the "Analyze Lead" button
4. View the detailed results

### Using curl

```bash
curl -X POST http://localhost:5000/api/analyze-lead \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I saw your ad and I am very interested in your product. Could you please send more details?"}'
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:5000/api/analyze-lead",
    json={"message": "Hi, I saw your ad and I am very interested in your product. Could you please send more details?"}
)

print(response.json())
``` 