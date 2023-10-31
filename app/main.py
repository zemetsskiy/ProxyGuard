from typing import Optional

from bson import json_util
from loguru import logger

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

# @app.get("/view_proxies")
# async def view_proxies(request: Request):
#     return templates.TemplateResponse("view_proxies.html", {"request": request})


@app.get("/get_proxies")
async def get_proxies(request: Request):
    proxies = list(db.proxies.find())

    for proxy in proxies:
        proxy_list = proxy.get('proxy_list', [])
        proxy_count = len(proxy_list)
        total_price = round(proxy.get('price', 0) * proxy_count, 3)
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
    cursor = db.proxies.find({"customer_name": customer_name})

    orders = []
    for order in cursor:
        proxy_list = order.get('proxy_list', [])
        proxy_count = len(proxy_list)
        price_per_proxy = order.get('price', 0)
        total_price = round(price_per_proxy * proxy_count, 2)
        purchase_date = order.get('purchase_date')
        duration_months = order.get('duration_months', 0)

        if purchase_date:
            expiration_date = purchase_date + timedelta(days=30 * duration_months)
            order['expiration_date'] = expiration_date.strftime('%Y-%m-%d')
            order['purchase_date'] = purchase_date.strftime('%Y-%m-%d')

        order['proxy_count'] = proxy_count
        order['price_per_proxy'] = price_per_proxy
        order['total_price'] = total_price
        order['margin'] = "SOON"
        order['profit'] = "SOON"

        orders.append(order)

    if orders:
        return templates.TemplateResponse("profile.html", {"request": request, "orders": orders, "customer_name": customer_name})

    return JSONResponse(content={}, status_code=404)


@app.delete("/delete_order/{customer_name}/{order_id}")
async def delete_order_by_id(customer_name: str, order_id: str):
    from bson import ObjectId
    db.proxies.delete_one({"customer_name": customer_name, "_id": ObjectId(order_id)})
    return {"message": "Order deleted successfully"}