import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time


def create_ollama_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retry))
    return session


def query_ollama(prompt):
    # Note: Changed port to 11434 (Ollama's default port)
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "stream": False
    }d

    try:
        session = create_ollama_session()
        response = session.post(url, json=payload)
        response.raise_for_status()
        json_response = response.json()
        # Extract only the response field
        return json_response.get('response', '')
    except requests.exceptions.ConnectionError as e:
        print(
            f"Connection Error: Make sure Ollama is running on port 11434. Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    # Test the connection
    result = query_ollama(input())
    if result:
        print(result)  # Will now print only the response text
