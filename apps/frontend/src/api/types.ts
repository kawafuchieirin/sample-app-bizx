export type Status = "todo" | "in_progress" | "done";
export type Priority = "high" | "medium" | "low";

export interface Board {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  board_id: string;
  title: string;
  description: string;
  status: Status;
  priority: Priority;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: Status;
  priority?: Priority;
  due_date?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: Status;
  priority?: Priority;
  due_date?: string | null;
  clear_due_date?: boolean;
}

export const STATUSES: Status[] = ["todo", "in_progress", "done"];

export const STATUS_LABEL: Record<Status, string> = {
  todo: "ToDo",
  in_progress: "進行中",
  done: "完了",
};

export const PRIORITY_LABEL: Record<Priority, string> = {
  high: "高",
  medium: "中",
  low: "低",
};
