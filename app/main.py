from typing import Optional

from bson import json_util
from loguru import logger

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
    return templates.TemplateResponse("view_proxies.html", {"request": request})


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
    return templates.TemplateResponse("view_proxies.html", {"request": request})


@app.get("/add_proxy")
async def add_proxy(request: Request):
    packages = db.packages.find({}, {"_id": 0, "package_name": 1})
    logger.info(packages)
    package_names = [package["package_name"] for package in packages]

    return templates.TemplateResponse("addition.html", {"request": request, "options": package_names})


@app.get("/add_proxy_package")
async def add_proxy(request: Request):
    return templates.TemplateResponse("add_proxy_package.html", {"request": request})


@app.post("/add_proxy_package")
async def add_proxy_package(request: Request,
                            package_name: str = Form(...),
                            price_per_proxy: float = Form(...)):

    proxy_package = {
        "package_name": package_name,
        "price_per_proxy": price_per_proxy
    }

    db.packages.insert_one(proxy_package)
    return templates.TemplateResponse("view_proxies.html", {"request": request})

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