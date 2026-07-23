import json
import os
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

# Завантажуємо ключ з файлу .env (для локального запуску)
load_dotenv()

app = FastAPI(title="Юридичний Бот API")

# Налаштовуємо CORS (щоб фронтенд Lovable міг звертатися до цього сервера)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізуємо клієнта Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# 1. Щоденний автономний генератор новин законодавства
@app.get("/api/news")
async def get_daily_news():
    today_str = date.today().strftime("%d липня %Y")

    prompt = f"""
    Ти — провідний юридичний аналітик України.
    Твоє завдання: згенерувати СВІЖИЙ та АКТУАЛЬНИЙ дайджест головних змін у законодавстві України станом на {today_str}.
    Згенеруй ТОЧНО ОДНУ картку-зведення про найважливішу реальну законну нововведеність чи дайджест за останні дні.

    Поверни відповідь СТРOГО у форматі JSON (без додаткового тексту, вступів чи ```json маркерів):
    {{
        "id": 1,
        "title": "Короткий заголовок головної зміни або дайджесту",
        "date": "{today_str}",
        "tags": ["#ПОДАТКИ", "#ВІЙСЬКОВИЙСТАН", "#БІЗНЕС"],
        "summary_title": "Короткий опис суті змін",
        "description": "Стислий опис закону, постанови або ініціативи, ухваленої ВР чи Кабміном.",
        "key_points": [
            "Теза 1: головне нововведення",
            "Теза 2: що змінюється для громадян/бізнесу",
            "Теза 3: терміни набрання чинності"
        ],
        "who_affected": [
            "Категорія осіб 1",
            "Категорія осіб 2"
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        news_data = json.loads(completion.choices[0].message.content)
        return {"news": [news_data]}

    except Exception as e:
        # Резервний варіант на випадок збою мережі/API
        return {
            "news": [
                {
                    "id": 1,
                    "title": f"Дайджест законодавства на {today_str}",
                    "date": today_str,
                    "tags": ["#ЗАКОНИ", "#УКРАЇНА"],
                    "summary_title": "Оновлення нормативно-правових актів",
                    "description": "Триває моніторинг нових постанов Кабміну та законопроєктів Верховної Ради.",
                    "key_points": [
                        "Аналітичний модуль оновлює бази даних",
                        "Дізнавайтеся деталі про нормативні акти на офіційних порталах",
                    ],
                    "who_affected": ["Громадяни України та бізнес"],
                }
            ]
        }


# 2. Модель та інструкція для чату
class UserMessage(BaseModel):
    message: str


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


# 3. Ендпоінт чату
@app.post("/api/chat")
async def chat_endpoint(data: UserMessage):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data.message},
            ],
            temperature=0.2,
        )

        reply = completion.choices[0].message.content
        return {"response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
