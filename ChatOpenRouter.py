import requests
import json

class OpenRouterLLM:
    """
    A class to wrap the OpenRouter API for interacting with LLMs.
    """

    def __init__(self, api_key, base_url="https://openrouter.ai/api/v1"):
        """
        Initializes the OpenRouterLLM object.

        Args:
            api_key (str): Your OpenRouter API key.
            base_url (str, optional): The base URL of the OpenRouter API. Defaults to "https://openrouter.ai/api/v1".
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, model, prompt, max_tokens=256, temperature=0.7, top_p=1.0, stream=False, stop=None, frequency_penalty=0.0, presence_penalty=0.0):
        """
        Generates text from the specified LLM.

        Args:
            model (str): The model to use (e.g., "openai/gpt-3.5-turbo").
            prompt (str): The input prompt.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 256.
            temperature (float, optional): Controls randomness. Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2) make it more deterministic. Defaults to 0.7.
            top_p (float, optional): Controls diversity via nucleus sampling. Defaults to 1.0.
            stream (bool, optional): Whether to stream the response. Defaults to False.
            stop (list, optional): A list of strings to stop generation when encountered. Defaults to None.
            frequency_penalty(float, optional): penalize new tokens based on their existing frequency in the text so far. Defaults to 0.0.
            presence_penalty(float, optional): penalize new tokens based on whether they appear in the text so far. Defaults to 0.0.

        Returns:
            str: The generated text, or None if an error occurred.
        """
        url = f"{self.base_url}/chat/completions"

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        if stop is not None:
            data["stop"] = stop

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            result = response.json()
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            else:
                return None  # Or raise an exception, depending on your error handling preference.
        except requests.exceptions.RequestException as e:
            print(f"Error during API call: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None
        except KeyError as e:
            print(f"Error accessing key in JSON response: {e}")
            return None