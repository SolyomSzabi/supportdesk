export type Role = "customer" | "agent";
export type Status = "open" | "in_progress" | "resolved" | "closed";
export type Priority = "" | "low" | "medium" | "high" | "urgent";
export type Category = "" | "billing" | "technical" | "account" | "other";

export type Me = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  role: Role;
  company: string | null;
};

export type Reply = {
  id: number;
  author: string;
  body: string;
  created_at: string;
};

export type Ticket = {
  id: number;
  title: string;
  description: string;
  status: Status;
  priority: Priority;
  category: Category;
  ai_summary: string;
  company: string;
  created_by: string;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  replies: Reply[];
};

export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export const STATUS_LABELS: Record<Status, string> = {
  open: "Open",
  in_progress: "In progress",
  resolved: "Resolved",
  closed: "Closed",
};
