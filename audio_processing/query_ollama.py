import os
import sqlite3
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "database/chat_history_ollama.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history_ollama (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def add_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history_ollama (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()


def get_conversation_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history_ollama ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


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
    # Retrieve conversation from DB
    history = get_conversation_history()

    system_prompt = ("You are a friendly and supportive speech therapist who helps users improve their "
                     "communication skills with patience, humor, and understanding. You work with both children "
                     "and adults, including individuals with Down syndrome, autism, and other speech or writing "
                     "challenges. You are a great listener and always provide encouragement. "
                     "When you detect pronunciation or spelling difficulties, you help the user review and correct them "
                     "in a supportive and engaging way, making learning fun and effective. "
                     "Always spell words correctly and encourage the user to repeat them.")
    # Build the full conversation: system, past messages, new user message
    conversation_text = f"system: {system_prompt}\n"
    for msg in history:
        conversation_text += f"{msg['role']}: {msg['content']}\n"
    conversation_text += f"user: {prompt}"

    payload = {
        "model": "phi4:latest",
        "prompt": conversation_text,
        "stream": False,
        "temperature": 0.7,  # Ajuste conforme necessário
        "max_tokens": 20
    }

    try:
        session = create_ollama_session()
        response = session.post(url, json=payload)
        response.raise_for_status()
        json_response = response.json()
        answer = json_response.get('response', '')
        # Log new messages to the DB
        add_message("user", prompt)
        add_message("assistant", answer)
        return answer
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    init_db()
    # Test the connection
    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            print("Goodbye! Have a great day!")
            break
        result = query_ollama(prompt)
        if result:
            print(f"Ollama: {result}")
