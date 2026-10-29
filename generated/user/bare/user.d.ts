type DateTime = string;

interface User {
  id: string;
  name: string;
  email?: string;
  age?: number;
  createdAt: DateTime;
}
