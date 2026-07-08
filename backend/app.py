import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from backend.db import init_db
from backend.routers import goals, tree, chat, journal, passport

init_db()

app = FastAPI(title="MoneyTree", version="0.1.0")

app.include_router(goals.router)
app.include_router(tree.router)
app.include_router(chat.router)
app.include_router(journal.router)
app.include_router(passport.router)

frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
def index():
    return FileResponse(str(frontend_dir / "index.html"))
