from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(Text, nullable=False)
    purchase_date = Column(Date, nullable=False)
    subscription_duration = Column(Integer, nullable=False)  # продолжительность подписки в месяцах
    price = Column(Integer, nullable=False)  # цена
    proxy_package = Column(Text, nullable=False)
