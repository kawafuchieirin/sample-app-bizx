import type { Board, Priority, Status, Task, TaskCreate, TaskUpdate } from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface ListTasksOptions {
  status?: Status;
  sort?: "due" | "priority";
  priority?: Priority;
}

export const api = {
  listBoards: (token: string) => request<Board[]>("/boards", token),

  createBoard: (token: string, name: string) =>
    request<Board>("/boards", token, { method: "POST", body: JSON.stringify({ name }) }),

  updateBoard: (token: string, id: string, name: string) =>
    request<Board>(`/boards/${id}`, token, { method: "PATCH", body: JSON.stringify({ name }) }),

  deleteBoard: (token: string, id: string) =>
    request<void>(`/boards/${id}`, token, { method: "DELETE" }),

  listTasks: (token: string, boardId: string, opts: ListTasksOptions = {}) => {
    const params = new URLSearchParams();
    if (opts.status) params.set("status", opts.status);
    if (opts.sort) params.set("sort", opts.sort);
    const qs = params.toString();
    return request<Task[]>(`/boards/${boardId}/tasks${qs ? `?${qs}` : ""}`, token);
  },

  createTask: (token: string, boardId: string, data: TaskCreate) =>
    request<Task>(`/boards/${boardId}/tasks`, token, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (token: string, taskId: string, data: TaskUpdate) =>
    request<Task>(`/tasks/${taskId}`, token, { method: "PATCH", body: JSON.stringify(data) }),

  deleteTask: (token: string, taskId: string) =>
    request<void>(`/tasks/${taskId}`, token, { method: "DELETE" }),
};
