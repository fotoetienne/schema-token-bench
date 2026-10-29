from datetime import datetime
from typing import Literal, NotRequired, TypedDict


# An attendee's reply to an invitation.
ResponseStatus = Literal[
    "NEEDS_ACTION",  # Has not replied.
    "ACCEPTED",
    "DECLINED",
    "TENTATIVE",
]


class Attendee(TypedDict):
    """A person invited to an event."""

    email: str
    name: NotRequired[str]
    response: ResponseStatus
    optional: bool  # Whether attendance is optional.


class Event(TypedDict):
    """A calendar event."""

    id: str
    title: str
    description: NotRequired[str]
    location: NotRequired[str]  # Room name, address, or meeting URL.
    start: datetime
    end: datetime
    attendees: list[Attendee]
    organizer: str  # Email of the organizer.


class TimeSlot(TypedDict):
    """A window of time when everyone is free."""

    start: datetime
    end: datetime


class EventInput(TypedDict):
    """Fields for creating or updating an event."""

    title: str
    description: NotRequired[str]
    location: NotRequired[str]
    start: datetime
    end: datetime
    attendee_emails: list[str]  # People to invite.


def list_events(
    start: datetime,
    end: datetime,
    query: str | None = None,
    limit: int | None = None,
) -> list[Event]:
    """List events that overlap a time range, soonest first.

    Args:
        start: Start of the range, inclusive.
        end: End of the range, exclusive.
        query: Only return events whose title or description matches.
        limit: Maximum number of events to return. Defaults to 50.
    """


def get_event(id: str) -> Event:
    """Fetch a single event by ID."""


def create_event(event: EventInput) -> Event:
    """Create an event and send invitations to its attendees."""


def update_event(id: str, event: EventInput) -> Event:
    """Replace an event's details. Attendees are notified of changes."""


def delete_event(id: str) -> bool:
    """Cancel an event and notify attendees. Returns false if it did not exist."""


def respond_to_event(
    id: str,
    response: ResponseStatus,
    comment: str | None = None,
) -> Event:
    """Reply to an invitation on behalf of the current user.

    Args:
        comment: Optional note sent to the organizer.
    """


def find_free_time(
    attendee_emails: list[str],
    duration_minutes: int,
    start: datetime,
    end: datetime,
) -> list[TimeSlot]:
    """Find time slots when all attendees are free.

    Args:
        duration_minutes: Length of the meeting.
        start: Earliest acceptable start.
        end: Latest acceptable end.
    """
