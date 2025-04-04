from ChatOpenRouter import OpenRouterLLM

import os
import nltk
import time
import json
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

# One-time download for VADER
nltk.download("vader_lexicon")

# Set OpenRouter key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set. Please set it in your .env file.")
# Set OpenRouter model
openrouter_model = "deepseek/deepseek-chat-v3-0324:free"

# Define the response model schema
class LeadScore(BaseModel):
    score: int
    justification: str

# 1. Function to analyze sentiment
def get_sentiment_score(message):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(message)
    compound = sentiment["compound"]
    if compound >= 0.5:
        label = "Very Positive"
    elif compound >= 0.1:
        label = "Positive"
    elif compound > -0.1:
        label = "Neutral"
    elif compound <= -0.5:
        label = "Very Negative"
    else:
        label = "Negative"
    return compound, label

# Function to extract JSON from text
def extract_json(text):
    """Extract JSON from text, handling various formats."""
    # Try to find JSON in the response
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        json_str = text[json_start:json_end]
        try:
            # Parse the JSON
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If direct parsing fails, try to clean the string
            # Remove any markdown code block indicators
            json_str = json_str.replace('```json', '').replace('```', '')
            # Remove any leading/trailing whitespace
            json_str = json_str.strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
    return None

# 2. Setup OpenRouter LLM
def create_llm_with_retry(max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            llm = OpenRouterLLM(api_key=api_key)
            # Test the connection with a simple prompt
            test_response = llm.generate(
                model=openrouter_model,
                prompt="Hello, this is a test message.Who are you?",
                max_tokens=100,
                temperature=0.2
            )
            if test_response:
                return llm
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to OpenRouter after {max_retries} attempts: {str(e)}")
                raise

llm = create_llm_with_retry()

# 3. Lead Analysis Function
def analyze_lead(message):
    prompt = f"""You are an expert lead scoring assistant. Your task is to analyze customer messages and determine their likelihood of conversion.

Message to analyze:
"{message}"

Please evaluate this message and provide a JSON response with:
1. A 'score' (an integer between 0 and 100), where:
   - 0: No chance of conversion
   - 50: Neutral interest
   - 100: Guaranteed conversion
2. A 'justification' (a brief explanation of how you arrived at that score)

IMPORTANT: Your response must be a valid JSON object with exactly this structure:
{{"score": <integer>, "justification": "<string>"}}

Do not include any additional text, explanations, or markdown formatting outside the JSON object.
Focus on:
- Level of interest expressed
- Specificity of the inquiry
- Urgency or timeline mentioned
- Request for information or next steps
- Overall engagement level"""

    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            gpt_response = llm.generate(
                model=openrouter_model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.2
            )
            if not gpt_response:
                raise ValueError("Empty response from model")
            
            # Extract and parse JSON
            data = extract_json(gpt_response)
            
            if data:
                # Validate against our Pydantic model
                lead_score = LeadScore(**data)
                return lead_score
            else:
                print(f"Attempt {attempt+1}: No valid JSON found in response. Retrying...")
                print("Raw response:", gpt_response)
                if attempt == max_retries - 1:
                    # Return a default response on final attempt
                    return LeadScore(score=50, justification="Unable to analyze due to technical issues.")
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to get GPT response after {max_retries} attempts: {str(e)}")
                # Return a default response
                return LeadScore(score=50, justification="Error during analysis.")
    
    # Fallback (should never reach here)
    return LeadScore(score=50, justification="Unable to analyze due to technical issues.")

# 4. Final Lead Score Function
def get_composite_lead_score(message):
    # Sentiment analysis
    compound_score, sentiment_label = get_sentiment_score(message)

    # GPT analysis with structured output
    lead_score = analyze_lead(message)
    
    # Weighted Composite Score
    # GPT gets 70% weight, Sentiment gets 30%
    sentiment_scaled_score = int((compound_score + 1) * 50)  # scale from -1:1 → 0:100
    final_score = int(lead_score.score * 0.7 + sentiment_scaled_score * 0.3)

    # Final Output with improved formatting
    print("\n=== Lead Analysis ===")
    print(f"Original Message: {message}")
    print(f"Sentiment Analysis: {sentiment_label} (Compound Score: {compound_score:.2f})")
    print(f"AI Analysis Score: {lead_score.score}/100")
    print(f"Final Composite Score: {final_score}/100")
    print("\nAI Justification:")
    print(lead_score.justification)
    print("=" * 50)
    
    # Return structured data
    return {
        "message": message,
        "sentiment": {
            "label": sentiment_label,
            "compound_score": compound_score
        },
        "ai_analysis": {
            "score": lead_score.score,
            "justification": lead_score.justification
        },
        "composite_score": final_score
    }


if __name__ == "__main__":
    # Test examples
    test_messages = [
        "Hi, I saw your ad and I'm very interested in your product. Could you please send more details?",
        "We need a solution for our inventory management. Can you provide pricing information?",
        "Not interested at this time, please remove me from your list.",
        "I'm the CTO of a mid-sized company and we're looking for an enterprise solution. Can we schedule a demo?"
    ]
    
    results = []
    for message in test_messages:
        result = get_composite_lead_score(message)
        results.append(result)
    
    # Print summary of all results
    print("\n=== Summary of All Results ===")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Message: {result['message'][:50]}...")
        print(f"Sentiment: {result['sentiment']['label']}")
        print(f"AI Score: {result['ai_analysis']['score']}/100")
        print(f"Composite Score: {result['composite_score']}/100")
    
    # Print all results as JSON
    print("\n=== All Results as JSON ===")
    print(json.dumps(results, indent=2)) 