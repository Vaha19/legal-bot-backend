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

MODEL_NAME = "llama-3.1-70b-versatile"


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

    prompt = f"""
    You must generate legal news for Ukraine for {today_str} in category "{random_category}".
    Respond strictly in valid json format without markdown codeblocks or extra text.

    Json structure:
    {{
        "id": 1,
        "title": "Заголовок реальної новини або зміни",
        "date": "{today_str}",
        "tags": ["#ЗАКОНИ", "#УКРАЇНА"],
        "summary_title": "Короткий опис суті змін",
        "description": "Детальний опис закону чи постанови Кабміну",
        "key_points": [
            "Основна суть нововведення",
            "Що змінюється для громадян та бізнесу",
            "Дата набрання чинності"
        ],
        "who_affected": [
            "Фізичні особи",
            "Підприємці"
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful legal assistant. Always output valid json.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )

        content = completion.choices[0].message.content
        news_data = json.loads(content)
        return {"news": [news_data]}

    except Exception as e:
        print("ERROR /api/news:", str(e))
        traceback.print_exc()
        return {
            "news": [
                {
                    "id": 1,
                    "title": f"Помилка запиту: {str(e)}",
                    "date": today_str,
                    "tags": ["#ПОМИЛКА"],
                    "summary_title": "Деталі помилки запиту до Groq",
                    "description": "Перевірте логи хостингу Render.",
                    "key_points": [str(e)],
                    "who_affected": ["Розробник"],
                }
            ]
        }


# 2. Петиції
@app.get("/api/petitions")
async def get_hot_petitions():
    today_str = get_ukrainian_date()

    prompt = f"""
    Generate 3 active or controversial petitions in Ukraine for {today_str}.
    Respond strictly in valid json format.

    Json structure:
    {{
        "petitions": [
            {{
                "id": 1,
                "title": "Заголовок петиції",
                "author": "Ініціатор",
                "target": "Президенту України",
                "votes_count": "21340 / 25000",
                "status": "Триває збір підписів",
                "tags": ["#СКАНДАЛ", "#БЮДЖЕТ"],
                "essence": "Суть петиції",
                "arguments_for": "Аргумент за",
                "arguments_against": "Аргумент проти"
            }}
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a social analyst. Always output valid json.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
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
                    "title": f"Помилка запиту: {str(e)}",
                    "author": "Система",
                    "target": "Адмін",
                    "votes_count": "0 / 25000",
                    "status": "Помилка",
                    "tags": ["#ПОМИЛКА"],
                    "essence": f"Деталі: {str(e)}",
                    "arguments_for": "-",
                    "arguments_against": "-",
                }
            ]
        }


# 3. Аналіз діяча
class PersonRequest(BaseModel):
    name: str


@app.post("/api/analyze-person")
async def analyze_person(data: PersonRequest):
    prompt = f"""
    Analyze political or public figure in Ukraine: "{data.name}".
    Respond strictly in valid json format in Ukrainian.

    Json structure:
    {{
        "person_name": "{data.name}",
        "overall_score": 65,
        "positive_score": 60,
        "negative_score": 40,
        "summary": "Детальний підсумок про діяльність та постать.",
        "good_deeds": ["Конкретний позитивний факт 1", "Конкретний позитивний факт 2"],
        "bad_deeds": ["Конкретна критика чи скандал 1", "Конкретна критика чи скандал 2"]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a political analyst. Output strictly valid json.",
                },
                {"role": "user", "content": prompt},
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
            "overall_score": 0,
            "positive_score": 0,
            "negative_score": 0,
            "summary": f"Помилка під час аналізу: {str(e)}",
            "good_deeds": ["Перевірте GROQ_API_KEY"],
            "bad_deeds": ["Перевірте логи Render"],
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
            model=MODEL_NAME,
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
