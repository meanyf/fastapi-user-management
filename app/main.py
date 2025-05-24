#main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import engine, Base, ensure_database_exists, save_users, get_users, get_user_from_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.future import select
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from app import models
import httpx
from app.models import User

templates = Jinja2Templates(directory="templates")
   
async def fetch_users(batch_size):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://randomuser.me/api/?results={batch_size}")
        response.raise_for_status()
        data = response.json()
        users_data = data["results"]
    users = [User.from_api_data(user) for user in users_data]
    return users
 
async def fetch_and_save_users(cnt: int, batch_size: int = 500):
    full_batches = cnt // batch_size
    remaining = cnt % batch_size

    for _ in range(full_batches):
        users = await fetch_users(batch_size)
        await save_users(users)

    if remaining:
        users = await fetch_users(batch_size)
        await save_users(users)
 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Проверка и создание базы, если нужно
    await ensure_database_exists()

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Загрузка начальных данных (опционально)
    await fetch_and_save_users(1000)

    yield
    # Код, который выполняется при завершении (shutdown) 
    # Можно оставить пустым или добавить очистку ресурсов

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, page: int = 1, limit: int = 20):
    users, page, total_pages = await get_users(page, limit)
    return templates.TemplateResponse(request, "users.html", {
        "request": request,
        "users": users,
        "page": page,
        "total_pages": total_pages,
        "limit": limit
    })

@app.get("/homepage/random", response_class=HTMLResponse)
async def get_random_user(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://randomuser.me/api/")
        if response.status_code != 200:
            return HTMLResponse(content="<h3>Ошибка при получении данных</h3>", status_code=500)

        data = response.json()["results"][0]

        user = User.from_api_data(data)

        return templates.TemplateResponse(request, "random_user.html", {
            "request": request,
            "user": user
            })

@app.get("/homepage/{user_id}", response_class=HTMLResponse)
async def get_user(user_id: int, request: Request):
    user = await get_user_from_db(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(request, "user.html", {
        "request": request,
        "user": user
    })

    
@app.post("/load")
async def load_users(count: int = Form(...)):
    await fetch_and_save_users(count)
    return RedirectResponse("/", status_code=303)