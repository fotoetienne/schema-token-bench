from datetime import datetime
from typing import Literal, NotRequired, TypedDict


class Money(TypedDict):
    """An amount of money in a specific currency."""

    amount: float  # Decimal amount, e.g. 19.99.
    currency: str  # ISO 4217 currency code, e.g. USD.


class Address(TypedDict):
    """A postal address."""

    line1: str  # Street address.
    line2: NotRequired[str]  # Apartment, suite, or unit.
    city: str
    region: NotRequired[str]  # State, province, or region.
    postal_code: str
    country: str  # ISO 3166-1 alpha-2 country code.


class Customer(TypedDict):
    """A person who places orders."""

    id: str
    email: str
    name: str  # Full name.
    phone: NotRequired[str]  # Phone number in E.164 format.
    shipping_address: NotRequired[Address]  # Default shipping address.
    created_at: datetime


class Product(TypedDict):
    """An item available for sale."""

    id: str
    sku: str  # Stock keeping unit.
    title: str
    description: NotRequired[str]  # Long-form description; may contain Markdown.
    price: Money  # Current list price.
    tags: list[str]  # Free-form labels used for search.
    in_stock: bool  # Whether at least one unit is available.


# Lifecycle state of an order.
OrderStatus = Literal[
    "PENDING",  # Created but not yet paid.
    "PAID",  # Payment captured.
    "SHIPPED",  # Handed to the carrier.
    "DELIVERED",  # Confirmed delivered.
    "CANCELLED",  # Cancelled before shipping.
]


class LineItem(TypedDict):
    """One product line within an order."""

    product: Product
    quantity: int  # Number of units; at least 1.
    unit_price: Money  # Price per unit at time of purchase.


class Order(TypedDict):
    """A customer's purchase."""

    id: str
    customer: Customer
    items: list[LineItem]  # Products in the order; never empty.
    status: OrderStatus
    total: Money  # Sum of all line items plus tax and shipping.
    notes: NotRequired[str]  # Free-text instructions from the customer.
    placed_at: datetime
    shipped_at: NotRequired[datetime]  # Set once status becomes SHIPPED.
