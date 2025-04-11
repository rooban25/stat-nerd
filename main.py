import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=JSONResponse)
async def chat(user_input: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Stat Nerd 🤓, a hilarious and sarcastic stat master. "
                        "Reply to the user's message with a funny, shocking, or fascinating statistic "
                        "in ONE sentence. Never start with 'Did you know' or sound formal. "
                        "Every response must be witty and feel like a joke wrapped in a fact. "
                        "Don't repeat stats. Tailor the stat to what the user said. Be confident and spicy."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.95,
            max_tokens=150,
        )
        bot_reply = response.choices[0].message.content.strip()

    except Exception as e:
        logging.error("OpenAI Error:", exc_info=True)
        bot_reply = "Oops, my stat brain just choked on a pie chart. Try again. 🥧"

    return {"reply": bot_reply}
