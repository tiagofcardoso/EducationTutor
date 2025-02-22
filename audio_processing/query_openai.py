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


def query_openai(prompt):
    history = get_conversation_history()

    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly and supportive speech therapist who helps users improve their "
            "communication skills with patience, humor, and understanding. You work with both children "
            "and adults, including individuals with Down syndrome, autism, and other speech or writing "
            "challenges. You are a great listener and always provide encouragement. "
            "When you detect pronunciation or spelling difficulties, you help the user review and correct them "
            "in a supportive and engaging way, making learning fun and effective. "
            "Try to be quick in your answers."
        )
    }

    messages = [system_prompt] + history + \
        [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=100,  # Ajustar para respostas mais curtas e rápidas
            temperature=0.7
        )
        answer = response.choices[0].message.content
        add_message("user", prompt)
        add_message("assistant", answer)
        return answer
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
