from datetime import datetime
from typing import NotRequired, TypedDict


class User(TypedDict):
    """A registered user account."""

    id: str  # Unique identifier.
    name: str  # Display name.
    email: NotRequired[str]  # Primary email address, if verified.
    age: NotRequired[int]  # Age in years.
    created_at: datetime  # When the account was created.
