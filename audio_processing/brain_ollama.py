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
    url = "http://localhost:11434/api/generate"

    system_prompt = ("You are a friendly and supportive speech therapist who helps users improve their "
                     "communication skills with patience, humor, and understanding. You work with both children "
                     "and adults, including individuals with Down syndrome, autism, and other speech or writing "
                     "challenges. You are a great listener and always provide encouragement. When you detect "
                     "pronunciation or spelling difficulties, you help the user review and correct them in a "
                     "supportive and engaging way, making learning fun and effective.")
    # Concatena a instrução do sistema com o prompt do usuário
    full_prompt = f"system: {system_prompt}\nuser: {prompt}"
    
    payload = {
        "model": "mistral:latest",
        "prompt": full_prompt,
        "stream": False,
        "temperature": 0.7,  # Ajuste conforme necessário
        "max_tokens": 100
    }

    try:
        session = create_ollama_session()
        response = session.post(url, json=payload)
        response.raise_for_status()
        json_response = response.json()
        # Extrai somente o campo response
        return json_response.get('response', '')
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    # Test the connection
    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            print("Goodbye! Have a great day!")
            break
        result = query_ollama(prompt)
        if result:
            print(f"Ollama: {result}")
