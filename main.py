import json
import os
import random
import traceback
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Юридичний Бот API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


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


# 1. Новини законодавства
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

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal analyst. Respond strictly in valid json format.",
                },
                {
                    "role": "user",
                    "content": f"""Згенеруй дайджест про оновлення законодавства України станом на {today_str} у сфері "{random_category}".
                    
                    Поверни json об'єкт:
                    {{
                        "id": 1,
                        "title": "Заголовок новини",
                        "date": "{today_str}",
                        "tags": ["#ЗАКОНИ", "#УКРАЇНА"],
                        "summary_title": "Короткий опис",
                        "description": "Стислий опис закону",
                        "key_points": ["Теза 1", "Теза 2", "Теза 3"],
                        "who_affected": ["Категорія 1", "Категорія 2"]
                    }}""",
                },
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return {"news": [json.loads(completion.choices[0].message.content)]}

    except Exception as e:
        print("ERROR /api/news:", str(e))
        traceback.print_exc()
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


# 2. Петиції
@app.get("/api/petitions")
async def get_hot_petitions():
    today_str = get_ukrainian_date()

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a social analyst. Respond strictly in valid json format.",
                },
                {
                    "role": "user",
                    "content": f"""Згенеруй 3 резонансні петиції в Україні станом на {today_str}.
                    
                    Поверни json об'єкт:
                    {{
                        "petitions": [
                            {{
                                "id": 1,
                                "title": "Заголовок петиції",
                                "author": "ПІБ Автора",
                                "target": "Президенту України",
                                "votes_count": "21340 / 25000",
                                "status": "Триває збір підписів",
                                "tags": ["#СКАНДАЛ", "#БЮДЖЕТ"],
                                "essence": "Опис суті петиції",
                                "arguments_for": "Аргумент за",
                                "arguments_against": "Аргумент проти"
                            }}
                        ]
                    }}""",
                },
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        print("ERROR /api/petitions:", str(e))
        traceback.print_exc()
        return {
            "petitions": [
                {
                    "id": 1,
                    "title": "Переспрямування місцевих бюджетів на ЗСУ",
                    "author": "Ініціативна група",
                    "target": "Президенту України",
                    "votes_count": "25000 / 25000",
                    "status": "На розгляді",
                    "tags": ["#БЮДЖЕТ", "#ЗСУ"],
                    "essence": "Вимога спрямувати кошти на закупівлю засобів для ЗСУ.",
                    "arguments_for": "Підтримка фронту",
                    "arguments_against": "Обмеження місцевого бюджету",
                }
            ]
        }


# 3. Аналіз діяча
class PersonRequest(BaseModel):
    name: str


@app.post("/api/analyze-person")
async def analyze_person(data: PersonRequest):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a political analyst. Output strictly valid json in Ukrainian.",
                },
                {
                    "role": "user",
                    "content": f"""Проаналізуй діяча: "{data.name}".
                    
                    Поверни json об'єкт:
                    {{
                        "person_name": "{data.name}",
                        "overall_score": 50,
                        "positive_score": 50,
                        "negative_score": 50,
                        "summary": "Короткий опис діяльності (2 речення)",
                        "good_deeds": ["Конкретна позитивна дія 1", "Конкретна позитивна дія 2"],
                        "bad_deeds": ["Конкретний негативний факт 1", "Конкретний негативний факт 2"]
                    }}""",
                },
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        print("ERROR /api/analyze-person:", str(e))
        traceback.print_exc()
        return {
            "person_name": data.name,
            "overall_score": 50,
            "positive_score": 50,
            "negative_score": 50,
            "summary": f"Аналіз для {data.name} тимчасово недоступний.",
            "good_deeds": ["Суспільна діяльність"],
            "bad_deeds": ["Публічна критика"],
        }


# 4. Чат
class UserMessage(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "Сервер працює!"}


@app.post("/api/chat")
async def chat_endpoint(data: UserMessage):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Ти — юридичний консультант з питань законодавства України.",
                },
                {"role": "user", "content": data.message},
            ],
            temperature=0.2,
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print("ERROR /api/chat:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
