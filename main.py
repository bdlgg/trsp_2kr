from pyexpat.errors import messages

from fastapi import FastAPI, Response, Header, Cookie, HTTPException
from typing import Optional

from fastapi.params import Depends
from itsdangerous import URLSafeTimedSerializer, BadSignature
from datetime import datetime
import uuid
import time



from models import UserCreate, CommonHeaders
app = FastAPI()

# данные для 3.2
sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

#3.1
@app.post("/create_user")
async def create_user(user: UserCreate):
    return user

#3.2
@app.get("/product/{product_id}")
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
        raise HTTPException(status_code=404, detail="Продукт не найден")

@app.get("/products/search")
async def search_products(
        keyword: str,
        category: Optional[str] = None,
        limit: int = 10
):
    results = []
    for product in sample_products:
        if keyword.lower() in product["name"].lower():
            if category is None or product["category"] == category:
                results.append(product)
    return results[:limit]

#5.1, 5.2, 5.3
SECRET_KEY = "ultra_suoer_key"
serializer = URLSafeTimedSerializer(SECRET_KEY)
SESSION_MAX_AGE = 300


@app.post("/login")
async def login(response: Response, username: str, password: str):
    if username == "user123" and password == "password123":
        user_id = str(uuid.uuid4())
        current_time = int(time.time())
        payload = f"{user_id}.{current_time}"
        token = serializer.dumps(payload)
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            secure=False,
            max_age=SESSION_MAX_AGE
        )
        return {"message": "Logged in"}
    raise HTTPException(status_code=401, detail="Неверные учетные данные")

@app.get("/profile")
async def get_profile(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Session expired")
    try:
        payload = serializer.loads(session_token, max_age=SESSION_MAX_AGE)
        user_id, last_activity_str = payload.split(".")
        last_activity = int(last_activity_str)
        current_time = int(time.time())
        diff = current_time - last_activity
        if diff >= 300:
            raise HTTPException(status_code=401, detail="Session expired")
        if diff >= 180:
            new_paiload = f"{user_id}.{current_time}"
            new_token = serializer.dumps(new_paiload)
            response.set_cookie(
                key="session_token",
                value=new_token,
                httponly=True,
                max_age=SESSION_MAX_AGE
            )
        return {"user_id": user_id, "message": "Profile accessed"}
    except (BadSignature, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session")


#5.4 и 5.5
async def get_common_headers(
        user_agent: Optional[str] = Header(default=None),
        accept_language: Optional[str] = Header(default=None)
) -> CommonHeaders:
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Неверный запрос отсутствуют заголовки")

@app.get("/headers")
async def read_headers(headers: CommonHeaders = Depends(get_common_headers)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/info")
async def get_info(headers: CommonHeaders = Depends(get_common_headers), response: Response = None):
    current_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = current_time
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }