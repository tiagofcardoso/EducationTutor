import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to your DB file (adjust if needed)
DB_PATH = os.path.join(os.path.dirname(__file__),
                       "database/chat_history_openai.db")

def init_db():
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

def add_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_conversation_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history ORDER BY id")
    messages = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return messages

def query_openai(prompt):
    # Retrieve saved conversation history
    history = get_conversation_history()

    # Start with a system prompt that sets the context
    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly and supportive speech therapist who helps users improve their "
            "communication skills with patience, humor, and understanding. You work with both children "
            "and adults, including individuals with Down syndrome, autism, and other speech or writing "
            "challenges. You are a great listener and always provide encouragement. "
            "When you detect pronunciation or spelling difficulties, you help the user review and correct them "
            "in a supportive and engaging way, making learning fun and effective. "
            "Always spell words correctly and encourage the user to repeat them."
        )
    }

    # Build a messages list combining system prompt + old conversation + new user prompt
    messages = [system_prompt] + history + [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = response.choices[0].message.content
        # Store the new messages
        add_message("user", prompt)
        add_message("assistant", answer)
        return answer
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    init_db()  # Ensure the table exists
    while True:
        prompt = input("Prompt (type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        result = query_openai(prompt)
        if result:
            print("Assistant:", result)
