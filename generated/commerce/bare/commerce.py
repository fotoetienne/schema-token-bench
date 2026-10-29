from datetime import datetime
from typing import Literal, NotRequired, TypedDict


class Money(TypedDict):
    amount: float
    currency: str


class Address(TypedDict):
    line1: str
    line2: NotRequired[str]
    city: str
    region: NotRequired[str]
    postal_code: str
    country: str


class Customer(TypedDict):
    id: str
    email: str
    name: str
    phone: NotRequired[str]
    shipping_address: NotRequired[Address]
    created_at: datetime


class Product(TypedDict):
    id: str
    sku: str
    title: str
    description: NotRequired[str]
    price: Money
    tags: list[str]
    in_stock: bool


OrderStatus = Literal["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]


class LineItem(TypedDict):
    product: Product
    quantity: int
    unit_price: Money


class Order(TypedDict):
    id: str
    customer: Customer
    items: list[LineItem]
    status: OrderStatus
    total: Money
    notes: NotRequired[str]
    placed_at: datetime
    shipped_at: NotRequired[datetime]
