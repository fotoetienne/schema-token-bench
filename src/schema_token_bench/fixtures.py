"""Benchmark schemas. Types are listed in dependency order so every format can
declare them top to bottom without forward references."""

from .model import Enum, EnumValue, Object, Operation, Schema, TypeRef, f, opt

USER = Schema(
    name="user",
    summary="One small object type",
    types=[
        Object(
            "User",
            doc="A registered user account.",
            fields=[
                f("id", "id", "Unique identifier."),
                f("name", "string", "Display name."),
                opt("email", "string", "Primary email address, if verified."),
                opt("age", "int", "Age in years."),
                f("createdAt", "datetime", "When the account was created."),
            ],
        ),
    ],
)

COMMERCE = Schema(
    name="commerce",
    summary="Seven related types: nesting, lists, an enum",
    types=[
        Object(
            "Money",
            doc="An amount of money in a specific currency.",
            fields=[
                f("amount", "float", "Decimal amount, e.g. 19.99."),
                f("currency", "string", "ISO 4217 currency code, e.g. USD."),
            ],
        ),
        Object(
            "Address",
            doc="A postal address.",
            fields=[
                f("line1", "string", "Street address."),
                opt("line2", "string", "Apartment, suite, or unit."),
                f("city", "string"),
                opt("region", "string", "State, province, or region."),
                f("postalCode", "string"),
                f("country", "string", "ISO 3166-1 alpha-2 country code."),
            ],
        ),
        Object(
            "Customer",
            doc="A person who places orders.",
            fields=[
                f("id", "id"),
                f("email", "string"),
                f("name", "string", "Full name."),
                opt("phone", "string", "Phone number in E.164 format."),
                opt("shippingAddress", "Address", "Default shipping address."),
                f("createdAt", "datetime"),
            ],
        ),
        Object(
            "Product",
            doc="An item available for sale.",
            fields=[
                f("id", "id"),
                f("sku", "string", "Stock keeping unit."),
                f("title", "string"),
                opt("description", "string", "Long-form description; may contain Markdown."),
                f("price", "Money", "Current list price."),
                f("tags", "[string]", "Free-form labels used for search."),
                f("inStock", "bool", "Whether at least one unit is available."),
            ],
        ),
        Enum(
            "OrderStatus",
            doc="Lifecycle state of an order.",
            values=[
                EnumValue("PENDING", "Created but not yet paid."),
                EnumValue("PAID", "Payment captured."),
                EnumValue("SHIPPED", "Handed to the carrier."),
                EnumValue("DELIVERED", "Confirmed delivered."),
                EnumValue("CANCELLED", "Cancelled before shipping."),
            ],
        ),
        Object(
            "LineItem",
            doc="One product line within an order.",
            fields=[
                f("product", "Product"),
                f("quantity", "int", "Number of units; at least 1."),
                f("unitPrice", "Money", "Price per unit at time of purchase."),
            ],
        ),
        Object(
            "Order",
            doc="A customer's purchase.",
            fields=[
                f("id", "id"),
                f("customer", "Customer"),
                f("items", "[LineItem]", "Products in the order; never empty."),
                f("status", "OrderStatus"),
                f("total", "Money", "Sum of all line items plus tax and shipping."),
                opt("notes", "string", "Free-text instructions from the customer."),
                f("placedAt", "datetime"),
                opt("shippedAt", "datetime", "Set once status becomes SHIPPED."),
            ],
        ),
    ],
)

CALENDAR = Schema(
    name="calendar",
    summary="Seven agent tools (operations) plus the types they use",
    types=[
        Enum(
            "ResponseStatus",
            doc="An attendee's reply to an invitation.",
            values=[
                EnumValue("NEEDS_ACTION", "Has not replied."),
                EnumValue("ACCEPTED"),
                EnumValue("DECLINED"),
                EnumValue("TENTATIVE"),
            ],
        ),
        Object(
            "Attendee",
            doc="A person invited to an event.",
            fields=[
                f("email", "string"),
                opt("name", "string"),
                f("response", "ResponseStatus"),
                f("optional", "bool", "Whether attendance is optional."),
            ],
        ),
        Object(
            "Event",
            doc="A calendar event.",
            fields=[
                f("id", "id"),
                f("title", "string"),
                opt("description", "string"),
                opt("location", "string", "Room name, address, or meeting URL."),
                f("start", "datetime"),
                f("end", "datetime"),
                f("attendees", "[Attendee]"),
                f("organizer", "string", "Email of the organizer."),
            ],
        ),
        Object(
            "TimeSlot",
            doc="A window of time when everyone is free.",
            fields=[f("start", "datetime"), f("end", "datetime")],
        ),
        Object(
            "EventInput",
            doc="Fields for creating or updating an event.",
            is_input=True,
            fields=[
                f("title", "string"),
                opt("description", "string"),
                opt("location", "string"),
                f("start", "datetime"),
                f("end", "datetime"),
                f("attendeeEmails", "[string]", "People to invite."),
            ],
        ),
    ],
    operations=[
        Operation(
            "listEvents",
            doc="List events that overlap a time range, soonest first.",
            params=[
                f("start", "datetime", "Start of the range, inclusive."),
                f("end", "datetime", "End of the range, exclusive."),
                opt("query", "string", "Only return events whose title or description matches."),
                opt("limit", "int", "Maximum number of events to return. Defaults to 50."),
            ],
            returns=TypeRef("Event", is_list=True),
        ),
        Operation(
            "getEvent",
            doc="Fetch a single event by ID.",
            params=[f("id", "id")],
            returns=TypeRef("Event"),
        ),
        Operation(
            "createEvent",
            doc="Create an event and send invitations to its attendees.",
            params=[f("event", "EventInput")],
            returns=TypeRef("Event"),
            is_mutation=True,
        ),
        Operation(
            "updateEvent",
            doc="Replace an event's details. Attendees are notified of changes.",
            params=[f("id", "id"), f("event", "EventInput")],
            returns=TypeRef("Event"),
            is_mutation=True,
        ),
        Operation(
            "deleteEvent",
            doc="Cancel an event and notify attendees. Returns false if it did not exist.",
            params=[f("id", "id")],
            returns=TypeRef("bool"),
            is_mutation=True,
        ),
        Operation(
            "respondToEvent",
            doc="Reply to an invitation on behalf of the current user.",
            params=[
                f("id", "id"),
                f("response", "ResponseStatus"),
                opt("comment", "string", "Optional note sent to the organizer."),
            ],
            returns=TypeRef("Event"),
            is_mutation=True,
        ),
        Operation(
            "findFreeTime",
            doc="Find time slots when all attendees are free.",
            params=[
                f("attendeeEmails", "[string]"),
                f("durationMinutes", "int", "Length of the meeting."),
                f("start", "datetime", "Earliest acceptable start."),
                f("end", "datetime", "Latest acceptable end."),
            ],
            returns=TypeRef("TimeSlot", is_list=True),
        ),
    ],
)

ALL = [USER, COMMERCE, CALENDAR]
