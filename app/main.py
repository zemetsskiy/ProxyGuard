from typing import Optional

from bson import json_util
from database import db
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add_proxy")
async def add_proxy(request: Request,
                    customer_name: str = Form(...),
                    purchase_date: str = Form(...),
                    duration_months: int = Form(...),
                    price: float = Form(...),
                    proxy_package: str = Form(...),
                    proxy_list: str = Form(...)):
    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
    proxy_array = proxy_list.split('\n')

    proxy_document = {
        "customer_name": customer_name,
        "purchase_date": purchase_date,
        "duration_months": duration_months,
        "price": price,
        "proxy_package": proxy_package,
        "proxy_list": proxy_array
    }
    db.proxies.insert_one(proxy_document)
    return {"message": "Proxy added successfully"}


@app.get("/add_proxy")
async def add_proxy(request: Request):
    return templates.TemplateResponse("addition.html", {"request": request})


@app.get("/view_proxies")
async def view_proxies(request: Request):
    return templates.TemplateResponse("view_proxies.html", {"request": request})


@app.get("/get_proxies")
async def get_proxies(request: Request, filter: Optional[str] = None):
    query = {}
    if filter:
        key, value = filter.split(':')
        query[key] = value
    proxies = list(db.proxies.find(query))
    return JSONResponse(content=json_util.dumps(proxies))