import json
import os
import random
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

# Завантажуємо ключ з файлу .env (для локального запуску)
load_dotenv()

app = FastAPI(title="Юридичний Бот API")

# Налаштовуємо CORS (щоб фронтенд Lovable та інші сервіси могли звертатися до API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізуємо клієнта Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Допоміжна функція для динамічної дати українською мовою
def get_ukrainian_date():
    months = {
        1: "січня",
        2: "лютого",
        3: "березня",
        4: "квітня",
        5: "травня",
        6: "червня",
        7: "липня",
        8: "серпня",
        9: "вересня",
        10: "жовтня",
        11: "листопада",
        12: "грудня",
    }
    today = date.today()
    return f"{today.day} {months[today.month]} {today.year}"


# 1. Щоденний генератор новин законодавства
@app.get("/api/news")
async def get_daily_news():
    today_str = get_ukrainian_date()

    categories = [
        "податки та бізнес (ФОП, мито, збори)",
        "військовий облік, мобілізація та соціальний захист військовослужбовців",
        "соціальні виплати, пенсії та допомога ВПО",
        "автомобільні закони, ПДР та штрафи",
        "цифровізація, Дія та судова система",
    ]
    random_category = random.choice(categories)

    prompt = f"""
    Ти — провідний юридичний аналітик України.
    Згенеруй СВІЖИЙ реальний дайджест або актуальну зміну у законодавстві України станом на {today_str}.
    Спеціалізація для цього запиту: {random_category}.

    Відповідай виключно у форматуванні JSON:
    {{
        "id": 1,
        "title": "Заголовок зміни у сфері: {random_category}",
        "date": "{today_str}",
        "tags": ["#ЗАКОНИ", "#УКРАЇНА"],
        "summary_title": "Короткий опис суті змін",
        "description": "Стислий опис закону або постанови Кабміну/ВР.",
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
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        news_data = json.loads(completion.choices[0].message.content)
        return {"news": [news_data]}

    except Exception as e:
        return {
            "news": [
                {
                    "id": 1,
                    "title": f"Дайджест законодавства на {today_str}",
                    "date": today_str,
                    "tags": ["#ЗАКОНИ", "#УКРАЇНА"],
                    "summary_title": "Оновлення нормативно-правових актів",
                    "description": "Моніторинг нових постанов Кабміну та законопроєктів ВРУ.",
                    "key_points": ["Оновлення баз даних у процесі"],
                    "who_affected": ["Громадяни України"],
                }
            ]
        }


# 2. Ендпоінт для найскандальніших/найрезонансніших петицій
@app.get("/api/petitions")
async def get_hot_petitions():
    today_str = get_ukrainian_date()

    prompt = f"""
    Ти — провідний суспільний та юридичний аналітик України.
    Згенеруй список з 3 найскандальніших або найважливіших петицій до Президента України чи ВРУ станом на {today_str}.

    Відповідай виключно у форматі JSON:
    {{
        "petitions": [
            {{
                "id": 1,
                "title": "Заголовок резонансної петиції",
                "author": "ПІБ Автора або Ініціативна група",
                "target": "Президенту України",
                "votes_count": "21,340 / 25,000",
                "status": "Триває збір підписів",
                "tags": ["#СКАНДАЛ", "#БЮДЖЕТ", "#РЕФОРМИ"],
                "essence": "Короткий опис у чому суть петиції та чому вона викликала резонанс.",
                "arguments_for": "Головний аргумент прибічників",
                "arguments_against": "Чому виник скандал або в чому контраргументи"
            }}
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        petitions_data = json.loads(completion.choices[0].message.content)
        return petitions_data

    except Exception as e:
        return {
            "petitions": [
                {
                    "id": 1,
                    "title": "Скасування необов'язкових витрат місцевих бюджетів під час війни",
                    "author": "Ініціативна група громадян",
                    "target": "Президенту України",
                    "votes_count": "25,000 / 25,000",
                    "status": "На розгляді",
                    "tags": ["#БЮДЖЕТ", "#ЗСУ"],
                    "essence": "Вимога спрямувати всі вільні кошти обласних та міських бюджетів на закупівлю Дронів та РЕБ для ЗСУ.",
                    "arguments_for": "Пріоритет національної безпеки та підтримки фронту",
                    "arguments_against": "Обмеження самоврядування та місцевих інфраструктурних проектів",
                }
            ]
        }


# 3. Аналіз публічного діяча/депутата
class PersonRequest(BaseModel):
    name: str


@app.post("/api/analyze-person")
async def analyze_person(data: PersonRequest):
    prompt = f"""
    Проаналізуй публічну діяльність, голосування та рішення політика або діяча України: "{data.name}".
    
    Надай об'єктивний аналіз у форматі JSON за такою схемою:
    - overall_score: число від 0 до 100 (загальний рейтинг корисності/надійності).
    - positive_score: число від 0 до 100 (відсоток позитиву).
    - negative_score: число від 0 до 100 (відсоток негативу, у сумі з positive_score має бути 100).
    - summary: стислий опис (2 речення) про постать {data.name}.
    - good_deeds: масив із 2 конкретних позитивних фактів чи законопроєктів.
    - bad_deeds: масив із 2 конкретних негативних фактів, критики чи скандалів.

    Формат відповіді (ТІЛЬКИ JSON):
    {{
        "person_name": "{data.name}",
        "overall_score": 45,
        "positive_score": 40,
        "negative_score": 60,
        "summary": "Конкретний опис особи...",
        "good_deeds": ["Реальний факт 1", "Реальний факт 2"],
        "bad_deeds": ["Реальний факт 1", "Реальний факт 2"]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Ти — незаангажований суспільно-юридичний аналітик. Відповідай виключно в форматі JSON українською мовою.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        analysis_data = json.loads(completion.choices[0].message.content)
        return analysis_data

    except Exception as e:
        return {
            "person_name": data.name,
            "overall_score": 50,
            "positive_score": 50,
            "negative_score": 50,
            "summary": f"Не вдалося згенерувати детальний аналіз для {data.name}. Спробуйте уточнити ім'я та прізвище.",
            "good_deeds": ["Публічна діяльність у системі управління"],
            "bad_deeds": ["Наявність суперечливих епізодів у кар'єрі"],
        }


# 4. Модель та інструкція для Чату
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
