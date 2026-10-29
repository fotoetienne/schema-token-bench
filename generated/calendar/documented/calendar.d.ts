/** ISO 8601 date-time string. */
type DateTime = string;

/** An attendee's reply to an invitation. */
type ResponseStatus =
  /** Has not replied. */
  | "NEEDS_ACTION"
  | "ACCEPTED"
  | "DECLINED"
  | "TENTATIVE";

/** A person invited to an event. */
interface Attendee {
  email: string;
  name?: string;
  response: ResponseStatus;
  /** Whether attendance is optional. */
  optional: boolean;
}

/** A calendar event. */
interface Event {
  id: string;
  title: string;
  description?: string;
  /** Room name, address, or meeting URL. */
  location?: string;
  start: DateTime;
  end: DateTime;
  attendees: Attendee[];
  /** Email of the organizer. */
  organizer: string;
}

/** A window of time when everyone is free. */
interface TimeSlot {
  start: DateTime;
  end: DateTime;
}

/** Fields for creating or updating an event. */
interface EventInput {
  title: string;
  description?: string;
  location?: string;
  start: DateTime;
  end: DateTime;
  /** People to invite. */
  attendeeEmails: string[];
}

/** List events that overlap a time range, soonest first. */
declare function listEvents(args: {
  /** Start of the range, inclusive. */
  start: DateTime;
  /** End of the range, exclusive. */
  end: DateTime;
  /** Only return events whose title or description matches. */
  query?: string;
  /** Maximum number of events to return. Defaults to 50. */
  limit?: number;
}): Event[];

/** Fetch a single event by ID. */
declare function getEvent(args: { id: string }): Event;

/** Create an event and send invitations to its attendees. */
declare function createEvent(args: { event: EventInput }): Event;

/** Replace an event's details. Attendees are notified of changes. */
declare function updateEvent(args: { id: string; event: EventInput }): Event;

/** Cancel an event and notify attendees. Returns false if it did not exist. */
declare function deleteEvent(args: { id: string }): boolean;

/** Reply to an invitation on behalf of the current user. */
declare function respondToEvent(args: {
  id: string;
  response: ResponseStatus;
  /** Optional note sent to the organizer. */
  comment?: string;
}): Event;

/** Find time slots when all attendees are free. */
declare function findFreeTime(args: {
  attendeeEmails: string[];
  /** Length of the meeting. */
  durationMinutes: number;
  /** Earliest acceptable start. */
  start: DateTime;
  /** Latest acceptable end. */
  end: DateTime;
}): TimeSlot[];
