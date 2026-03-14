from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="내 주변 병원 찾기")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

KAKAO_JS_API_KEY = os.getenv("KAKAO_JS_API_KEY", "")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY}
    )


@app.get("/chatbot")
async def chatbot(request: Request, department: str = ""):
    return templates.TemplateResponse(
        "chatbot.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "department": department}
    )


@app.get("/hospitals")
async def hospitals(request: Request, department: str = ""):
    return templates.TemplateResponse(
        "hospital_list.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "department": department}
    )


@app.get("/hospitals/{hospital_id}")
async def hospital_detail(request: Request, hospital_id: str):
    return templates.TemplateResponse(
        "hospital_detail.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "hospital_id": hospital_id}
    )
