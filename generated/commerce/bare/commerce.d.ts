type DateTime = string;

interface Money {
  amount: number;
  currency: string;
}

interface Address {
  line1: string;
  line2?: string;
  city: string;
  region?: string;
  postalCode: string;
  country: string;
}

interface Customer {
  id: string;
  email: string;
  name: string;
  phone?: string;
  shippingAddress?: Address;
  createdAt: DateTime;
}

interface Product {
  id: string;
  sku: string;
  title: string;
  description?: string;
  price: Money;
  tags: string[];
  inStock: boolean;
}

type OrderStatus = "PENDING" | "PAID" | "SHIPPED" | "DELIVERED" | "CANCELLED";

interface LineItem {
  product: Product;
  quantity: number;
  unitPrice: Money;
}

interface Order {
  id: string;
  customer: Customer;
  items: LineItem[];
  status: OrderStatus;
  total: Money;
  notes?: string;
  placedAt: DateTime;
  shippedAt?: DateTime;
}
