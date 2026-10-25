import type { Me, Page, Reply, Status, Ticket } from "./types";

const ACCESS_KEY = "supportdesk.access";
const REFRESH_KEY = "supportdesk.refresh";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

const readToken = (key: string): string | null => {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
};

const saveTokens = (access: string, refresh?: string) => {
  localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
};

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
};

export const hasToken = () => readToken(ACCESS_KEY) !== null;

// Turns DRF error bodies ({"detail": ...} or {"field": ["msg"]}) into one readable line.
const errorMessage = (body: unknown, fallback: string): string => {
  if (!body || typeof body !== "object") return fallback;
  const record = body as Record<string, unknown>;
  if (typeof record.detail === "string") return record.detail;
  const parts = Object.entries(record).map(([field, value]) => {
    const text = Array.isArray(value) ? value.join(" ") : String(value);
    return field === "non_field_errors" ? text : `${field}: ${text}`;
  });
  return parts.length ? parts.join(" ") : fallback;
};

const refreshAccessToken = async (): Promise<boolean> => {
  const refresh = readToken(REFRESH_KEY);
  if (!refresh) return false;
  const response = await fetch("/api/auth/token/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return false;
  const data = (await response.json()) as { access: string };
  saveTokens(data.access);
  return true;
};

const request = async <T>(path: string, init: RequestInit = {}, retry = true): Promise<T> => {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body) headers.set("Content-Type", "application/json");
  const access = readToken(ACCESS_KEY);
  if (access) headers.set("Authorization", `Bearer ${access}`);

  const response = await fetch(path, { ...init, headers });

  // The access token lives 30 minutes; on 401 we try the refresh token once.
  if (response.status === 401 && retry && (await refreshAccessToken())) {
    return request<T>(path, init, false);
  }

  const body: unknown = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) clearTokens();
    throw new ApiError(response.status, errorMessage(body, `Request failed (${response.status})`));
  }
  return body as T;
};

export const login = async (username: string, password: string) => {
  const tokens = await request<{ access: string; refresh: string }>(
    "/api/auth/token/",
    { method: "POST", body: JSON.stringify({ username, password }) },
    false,
  );
  saveTokens(tokens.access, tokens.refresh);
};

export const fetchMe = () => request<Me>("/api/me/");

export const fetchTickets = (params: Record<string, string>) => {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== ""));
  return request<Page<Ticket>>(`/api/tickets/?${query}`);
};

export const fetchTicket = (id: number) => request<Ticket>(`/api/tickets/${id}/`);

export const createTicket = (title: string, description: string) =>
  request<Ticket>("/api/tickets/", {
    method: "POST",
    body: JSON.stringify({ title, description }),
  });

export const updateStatus = (id: number, status: Status) =>
  request<Ticket>(`/api/tickets/${id}/`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });

export const sendReply = (id: number, body: string) =>
  request<Reply>(`/api/tickets/${id}/reply/`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });

export const suggestReply = (id: number) =>
  request<{ draft: string }>(`/api/tickets/${id}/suggest-reply/`, { method: "POST" });
