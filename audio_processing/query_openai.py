import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(
    dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "database/chat_history_openai.db")


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        raise


def add_message(role, content):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO history (role, content) VALUES (?, ?)",
                  (role, content))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao adicionar mensagem: {e}")
        raise


def get_conversation_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT role, content FROM history ORDER BY id")
        messages = [{"role": row[0], "content": row[1]}
                    for row in c.fetchall()]
        conn.close()
        return messages
    except sqlite3.Error as e:
        print(f"Erro ao obter histórico: {e}")
        return []


def clean_response_for_tts(text):
    """Simplified cleaning that focuses on natural speech flow"""
    import re

    # Basic cleanups
    text = re.sub(r'###|\*|\-|•', '', text)  # Remove markdown characters
    text = re.sub(r'\([^)]*\)', '', text)    # Remove parentheses and content
    text = re.sub(r'\n+', '. ', text)        # Convert newlines to periods
    text = re.sub(r'\s+', ' ', text)         # Normalize spaces

    # Make sure there's proper spacing around punctuation
    text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)

    # Remove any remaining special characters
    text = re.sub(r'[^\w\s.,!?;:]', ' ', text)

    return text.strip()


def query_openai(prompt):
    history = get_conversation_history()

    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly speech therapist. When responding: "
            "1. Use simple, conversational language. "
            "2. Speak in short, clear sentences. "
            "3. Avoid using special characters or formatting. "
            "4. Present information in a natural, flowing way. "
            "5. Give examples as part of the conversation. "
            "For example, instead of writing '- Sound of X:', say 'The sound of X is like in...'"
        )
    }

    messages = [system_prompt] + history + \
        [{"role": "user", "content": prompt}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )

        answer = response.choices[0].message.content
        clean_answer = clean_response_for_tts(answer)

        # Store original response in history
        add_message("user", prompt)
        add_message("assistant", answer)

        return clean_answer

    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return None


if __name__ == "__main__":
    init_db()
    while True:
        prompt = input("Prompt (type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        result = query_openai(prompt)
        if result:
            print("Assistant:", result)
