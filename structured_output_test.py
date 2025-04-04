import os
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import json
from ChatOpenRouter import OpenRouterLLM

# Load environment variables
load_dotenv()

# Define the model name
openrouter_model = "deepseek/deepseek-chat-v3-0324:free"

# Define the response model schema
class LeadScore(BaseModel):
    score: int
    justification: str

# Ensure the API key is available
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in your environment.")

# Create the OpenRouterLLM client
llm = OpenRouterLLM(api_key=OPENROUTER_API_KEY)

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

# Function to analyze a lead and return structured data
def analyze_lead(message):
    """Analyze a lead message and return structured data."""
    # Construct a prompt that clearly instructs the model to output a JSON matching the LeadScore schema
    prompt = (
        "You are an AI assistant tasked with evaluating a sales lead. "
        "Based on the following customer message, provide a JSON response that includes a 'score' (an integer between 0 and 100) "
        "and a 'justification' (a brief explanation of how you arrived at that score).\n\n"
        "IMPORTANT: Your response must be a valid JSON object with exactly this structure:\n"
        '{"score": <integer>, "justification": "<string>"}\n\n'
        "Do not include any additional text, explanations, or markdown formatting outside the JSON object.\n"
        "The score should be an integer between 0 and 100.\n\n"
        f"Customer Message: '{message}'"
    )

    try:
        # Generate response using the OpenRouterLLM
        response_text = llm.generate(
            model=openrouter_model,
            prompt=prompt,
            max_tokens=500,
            temperature=0.2
        )
        
        # Extract and parse JSON
        data = extract_json(response_text)
        
        if data:
            # Validate against our Pydantic model
            lead_score = LeadScore(**data)
            return lead_score
        else:
            print("No valid JSON found in response:")
            print(response_text)
            # Return a default response
            return LeadScore(score=50, justification="Unable to analyze due to technical issues.")
            
    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        # Return a default response
        return LeadScore(score=50, justification="Error during analysis.")

# Test the lead analysis
if __name__ == "__main__":
    # Test message
    test_message = "Hello, I need a solution for our inventory management. Can you provide pricing information?"
    
    # Analyze the lead
    result = analyze_lead(test_message)
    
    # Print the structured result
    print("\n=== Lead Analysis Result ===")
    print(f"Score: {result.score}/100")
    print(f"Justification: {result.justification}")
    
    # Print the raw JSON
    print("\n=== Raw JSON ===")
    print(json.dumps(result.dict(), indent=2))
