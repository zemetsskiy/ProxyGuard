from typing import Optional

from bson import json_util
from database import db
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

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

    for proxy in proxies:
        proxy_list = proxy.get('proxy_list', [])
        proxy_count = len(proxy_list)
        total_price = proxy.get('price', 0) * proxy_count
        purchase_date = proxy.get('purchase_date')
        duration_months = proxy.get('duration_months', 0)

        proxy['proxy_count'] = proxy_count
        proxy['total_price'] = total_price
        proxy['margin'] = "empty"
        proxy['profit'] = "empty"

        if purchase_date:
            expiration_date = purchase_date + timedelta(days=30 * duration_months)
            proxy['expiration_date'] = expiration_date

    return JSONResponse(content=json_util.dumps(proxies))


@app.get("/profile/{customer_name}")
async def get_profile_by_customer_name(request: Request, customer_name: str):
    customer_data = db.proxies.find_one({"customer_name": customer_name})

    proxy_list = customer_data.get('proxy_list', [])
    proxy_count = len(proxy_list)
    total_price = customer_data.get('price', 0) * proxy_count
    purchase_date = customer_data.get('purchase_date')
    duration_months = customer_data.get('duration_months', 0)

    if purchase_date:
        expiration_date = purchase_date + timedelta(days=30 * duration_months)
        customer_data['expiration_date'] = expiration_date.strftime('%Y-%m-%d')
        customer_data['purchase_date'] = purchase_date.strftime('%Y-%m-%d')

    customer_data['proxy_count'] = proxy_count
    customer_data['total_price'] = total_price
    customer_data['margin'] = "empty"
    customer_data['profit'] = "empty"

    if customer_data:
        print(customer_data)
        return templates.TemplateResponse("profile.html", {"request": request, "profile": customer_data})
        #return JSONResponse(content=json_util.dumps(customer_data))
    return JSONResponse(content={}, status_code=404)