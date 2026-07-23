import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from datetime import date

# Завантажуємо ключ з файлу .env
load_dotenv()

app = FastAPI(title="Юридичний Бот API")

@app.get("/api/news")
async def get_daily_news():
    today_str = date.today().strftime("%d липня %Y")
    
    # Тут можна збирати новини через RSS/Парсинг або запит до AI
    news_list = [
        {
            "id": 1,
            "title": "Зміни до Податкового кодексу України",
            "date": today_str,
            "tags": ["#TAXES", "#BUSINESS"],
            "summary_title": "Основні зміни до Податкового кодексу",
            "description": "Верховна Рада ухвалила закон №4215-IX, який запроваджує оновлення для платників податків з 1 серпня.",
            "key_points": [
                "Ставка податку на прибуток для великих підприємств зростає з 18% до 20%",
                "Спрощена система (3 група) — ставка залишається 5%",
                "Введено тимчасовий військовий збір 1.5% на доходи ФОП"
            ],
            "who_affected": [
                "Юридичних осіб із оборотом понад 40 млн грн"
            ]
        }
    ]
    return {"news": news_list}

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
        raise HTTPException(status_code=500, detail=str(e))
