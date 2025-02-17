from openai import OpenAI

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set OpenAI API key

def query_openai(prompt):
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly and supportive speech therapist who helps users improve their communication skills with patience, humor, and understanding. You work with both children and adults, including individuals with Down syndrome, autism, and other speech or writing challenges. You are a great listener and always provide encouragement. When you detect pronunciation or spelling difficulties, you help the user review and correct them in a supportive and engaging way, making learning fun and effective."
            },
            {"role": "user", "content": prompt}
        ])
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test the connection
    while True:
        prompt = input("Prompt (type 'exit' to quit): ")
        if prompt.lower() == 'exit':
            print("Goodbye! Have a great day!")
            break
        result = query_openai(prompt)
        if result:
            print(result)
