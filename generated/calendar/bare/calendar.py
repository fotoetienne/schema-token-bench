from datetime import datetime
from typing import Literal, NotRequired, TypedDict


ResponseStatus = Literal["NEEDS_ACTION", "ACCEPTED", "DECLINED", "TENTATIVE"]


class Attendee(TypedDict):
    email: str
    name: NotRequired[str]
    response: ResponseStatus
    optional: bool


class Event(TypedDict):
    id: str
    title: str
    description: NotRequired[str]
    location: NotRequired[str]
    start: datetime
    end: datetime
    attendees: list[Attendee]
    organizer: str


class TimeSlot(TypedDict):
    start: datetime
    end: datetime


class EventInput(TypedDict):
    title: str
    description: NotRequired[str]
    location: NotRequired[str]
    start: datetime
    end: datetime
    attendee_emails: list[str]


def list_events(
    start: datetime,
    end: datetime,
    query: str | None = None,
    limit: int | None = None,
) -> list[Event]: ...


def get_event(id: str) -> Event: ...


def create_event(event: EventInput) -> Event: ...


def update_event(id: str, event: EventInput) -> Event: ...


def delete_event(id: str) -> bool: ...


def respond_to_event(
    id: str,
    response: ResponseStatus,
    comment: str | None = None,
) -> Event: ...


def find_free_time(
    attendee_emails: list[str],
    duration_minutes: int,
    start: datetime,
    end: datetime,
) -> list[TimeSlot]: ...
