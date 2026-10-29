from datetime import datetime
from typing import NotRequired, TypedDict


class User(TypedDict):
    id: str
    name: str
    email: NotRequired[str]
    age: NotRequired[int]
    created_at: datetime
