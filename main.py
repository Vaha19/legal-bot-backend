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

#Щоденний генератор новин
@app.get("/api/news")
async def get_daily_news():
    today_str = date.today().strftime("%d липня %Y")

    # Додаємо вибір випадкової сфери, щоб новини змінювалися при оновленні
    categories = [
        "податки та бізнес (ФОП, мито, збори)",
        "військовий облік, мобілізація та соціальний захист військовослужбовців",
        "соціальні виплати, пенсії та допомога ВПО",
        "автомобільні закони, ПДР та штрафи",
        "цифровізація, дія та судова система",
    ]
    random_category = random.choice(categories)

    prompt = f"""
    Ти — провідний юридичний аналітик України.
    Згенеруй СВІЖИЙ реальний дайджест або актуальну зміну у законодавстві України станом на {today_str}.
    
    Спеціалізація для цього запиту: {random_category}.

    Поверни відповідь СТРOГО у форматі JSON (без додаткового тексту чи ```json):
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
            temperature=0.7,  # Збільшено для різноманітності відповідей
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
    
# Ендпоінт для найскандальніших/найрезонансніших петицій
@app.get("/api/petitions")
async def get_hot_petitions():
    today_str = get_ukrainian_date()

    prompt = f"""
    Ти — провідний суспільний та юридичний аналітик України.
    Твоє завдання: згенерувати список з 3 найскандальніших, найобговорюваніших або найважливіших петицій до Президента України або Верховної Ради за останній час станом на {today_str}.

    Поверни відповідь СТРOГО у формате JSON (без додаткового тексту чи ```json маркерів):
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
                    "title": "Моніторинг офіційних петицій",
                    "author": "Суспільні активісти",
                    "target": "Офіс Президента",
                    "votes_count": "25,000 / 25,000",
                    "status": "На розгляді",
                    "tags": ["#СУСПІЛЬСТВО"],
                    "essence": "Триває аналіз та оновлення реєстру актуальних петицій.",
                    "arguments_for": "Високий суспільний інтерес",
                    "arguments_against": "Потребує правової оцінки",
                }
            ]
        }
# 4. Модель для запиту аналізу діяча
class PersonRequest(BaseModel):
    name: str

@app.post("/api/analyze-person")
async def analyze_person(data: PersonRequest):
    prompt = f"""
    Ти — незаангажований суспільно-юридичний аналітик.
    Проаналізуй публічну діяльність, голосування, законопроєкти або висловлювання особи: "{data.name}".
    
    Оціни її діяльність за шкалою від 0 до 100 та надай об'єктивний баланс позитивних і негативних фактів.
    
    Поверни відповідь СТРOГО у форматі JSON (без додаткового тексту чи ```json):
    {{
        "person_name": "{data.name}",
        "overall_score": 75,
        "positive_score": 80,
        "negative_score": 20,
        "summary": "Короткий загальний висновок про діяльність людини (2-3 речення).",
        "good_deeds": [
            "Факт 1: Позитивна дія або корисний законопроєкт",
            "Факт 2: Публічна позиція чи корисна ініціатива"
        ],
        "bad_deeds": [
            "Факт 1: Зауваження, прогули або суперечливі голосування",
            "Факт 2: Критика або скандальні епізоди"
        ]
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        analysis_data = json.loads(completion.choices[0].message.content)
        return analysis_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка аналізу: {str(e)}")

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
