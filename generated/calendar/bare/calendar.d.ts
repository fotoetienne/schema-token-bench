type DateTime = string;

type ResponseStatus = "NEEDS_ACTION" | "ACCEPTED" | "DECLINED" | "TENTATIVE";

interface Attendee {
  email: string;
  name?: string;
  response: ResponseStatus;
  optional: boolean;
}

interface Event {
  id: string;
  title: string;
  description?: string;
  location?: string;
  start: DateTime;
  end: DateTime;
  attendees: Attendee[];
  organizer: string;
}

interface TimeSlot {
  start: DateTime;
  end: DateTime;
}

interface EventInput {
  title: string;
  description?: string;
  location?: string;
  start: DateTime;
  end: DateTime;
  attendeeEmails: string[];
}

declare function listEvents(args: {
  start: DateTime;
  end: DateTime;
  query?: string;
  limit?: number;
}): Event[];

declare function getEvent(args: { id: string }): Event;

declare function createEvent(args: { event: EventInput }): Event;

declare function updateEvent(args: { id: string; event: EventInput }): Event;

declare function deleteEvent(args: { id: string }): boolean;

declare function respondToEvent(args: {
  id: string;
  response: ResponseStatus;
  comment?: string;
}): Event;

declare function findFreeTime(args: {
  attendeeEmails: string[];
  durationMinutes: number;
  start: DateTime;
  end: DateTime;
}): TimeSlot[];
