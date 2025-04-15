import os
import requests
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

# Gemini API config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

if not GEMINI_API_KEY:
    raise ValueError("Missing Gemini API key!")

# Setup FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize chat history
chat_history = []

# Home page
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    # Uncomment the next line to reset chat every time
    # chat_history.clear()
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": chat_history})


from fastapi.responses import JSONResponse

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")

    headers = {"Content-Type": "application/json"}

    prompt = (
        "You are Stat Nerd 🤓, a hilarious and sarcastic stat master. "
        "Reply to the user's message with a funny, shocking, or fascinating statistic "
        "in ONE sentence. The stat should be related to one key word from the prompt."
        "Every response must be witty and feel like a joke wrapped in a fact. "
        "Don't repeat stats. Tailor the stat to what the user said. Be confident and spicy."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nUser: {user_input}"}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]

        chat_history.append(("User", user_input))
        chat_history.append(("Stat Nerd 🤓", bot_reply))
    except Exception as e:
        bot_reply = "Oops, my stat brain tripped over a pie chart again. Try me later. 🥧"
        chat_history.append(("User", user_input))
        chat_history.append(("Stat Nerd 🤓", bot_reply))

    return JSONResponse(content={"reply": bot_reply})
