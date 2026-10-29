/** ISO 8601 date-time string. */
type DateTime = string;

/** A registered user account. */
interface User {
  /** Unique identifier. */
  id: string;
  /** Display name. */
  name: string;
  /** Primary email address, if verified. */
  email?: string;
  /** Age in years. */
  age?: number;
  /** When the account was created. */
  createdAt: DateTime;
}
