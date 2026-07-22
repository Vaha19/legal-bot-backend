import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Завантажуємо ключ з файлу .env
load_dotenv()

app = FastAPI(title="Юридичний Бот API")

# Налаштовуємо CORS (щоб фронтенд Lovable міг звертатися до цього сервера)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел під час розробки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізуємо клієнта Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Описуємо формат даних, які чекаємо від Lovable
class UserMessage(BaseModel):
    message: str

# Інструкція для ШІ (як він має поводитися)
SYSTEM_PROMPT = """
Ти — професійний юридичний консультант з питань законодавства України. 
Твоє завдання:
1. Відповідати чітко, структуровано та зрозумілою мовою.
2. Посилатися на відповідні закони, кодекси та статті, коли це доцільно.
3. Якщо питання розмите — ввічливо уточни деталі.
"""

@app.get("/")
def home():
    return {"status": "Сервер працює!"}

@app.post("/api/chat")
async def chat_endpoint(data: UserMessage):
    try:
        # Відправляємо запит до моделі LLaMA через Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data.message}
            ],
            temperature=0.2, # Низька температура робить відповіді більш точними і строгими
        )
        
        reply = completion.choices[0].message.content
        return {"response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))