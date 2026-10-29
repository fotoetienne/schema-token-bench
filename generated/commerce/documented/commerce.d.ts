/** ISO 8601 date-time string. */
type DateTime = string;

/** An amount of money in a specific currency. */
interface Money {
  /** Decimal amount, e.g. 19.99. */
  amount: number;
  /** ISO 4217 currency code, e.g. USD. */
  currency: string;
}

/** A postal address. */
interface Address {
  /** Street address. */
  line1: string;
  /** Apartment, suite, or unit. */
  line2?: string;
  city: string;
  /** State, province, or region. */
  region?: string;
  postalCode: string;
  /** ISO 3166-1 alpha-2 country code. */
  country: string;
}

/** A person who places orders. */
interface Customer {
  id: string;
  email: string;
  /** Full name. */
  name: string;
  /** Phone number in E.164 format. */
  phone?: string;
  /** Default shipping address. */
  shippingAddress?: Address;
  createdAt: DateTime;
}

/** An item available for sale. */
interface Product {
  id: string;
  /** Stock keeping unit. */
  sku: string;
  title: string;
  /** Long-form description; may contain Markdown. */
  description?: string;
  /** Current list price. */
  price: Money;
  /** Free-form labels used for search. */
  tags: string[];
  /** Whether at least one unit is available. */
  inStock: boolean;
}

/** Lifecycle state of an order. */
type OrderStatus =
  /** Created but not yet paid. */
  | "PENDING"
  /** Payment captured. */
  | "PAID"
  /** Handed to the carrier. */
  | "SHIPPED"
  /** Confirmed delivered. */
  | "DELIVERED"
  /** Cancelled before shipping. */
  | "CANCELLED";

/** One product line within an order. */
interface LineItem {
  product: Product;
  /** Number of units; at least 1. */
  quantity: number;
  /** Price per unit at time of purchase. */
  unitPrice: Money;
}

/** A customer's purchase. */
interface Order {
  id: string;
  customer: Customer;
  /** Products in the order; never empty. */
  items: LineItem[];
  status: OrderStatus;
  /** Sum of all line items plus tax and shipping. */
  total: Money;
  /** Free-text instructions from the customer. */
  notes?: string;
  placedAt: DateTime;
  /** Set once status becomes SHIPPED. */
  shippedAt?: DateTime;
}
