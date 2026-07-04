import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, ApiError } from "../api/client";
import type { Priority, Status, Task } from "../api/types";
import { PRIORITY_LABEL, STATUS_LABEL, STATUSES } from "../api/types";
import { useToken } from "../hooks/useToken";

export default function BoardPage() {
  const token = useToken();
  const { boardId = "" } = useParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // New-task form state.
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [dueDate, setDueDate] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .listTasks(token, boardId, { sort: "due" })
      .then((data) => active && setTasks(data))
      .catch((e: ApiError) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [token, boardId]);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    try {
      const task = await api.createTask(token, boardId, {
        title: trimmed,
        priority,
        due_date: dueDate || null,
      });
      setTasks((prev) => [...prev, task]);
      setTitle("");
      setDueDate("");
      setPriority("medium");
    } catch (err) {
      setError((err as ApiError).message);
    }
  };

  const moveTask = async (task: Task, status: Status) => {
    try {
      const updated = await api.updateTask(token, task.id, { status });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err) {
      setError((err as ApiError).message);
    }
  };

  const onDelete = async (id: string) => {
    try {
      await api.deleteTask(token, id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      setError((err as ApiError).message);
    }
  };

  if (loading) return <p className="center">読み込み中…</p>;

  return (
    <section className="board">
      <p>
        <Link to="/">← ボード一覧</Link>
      </p>
      {error && <p className="error">{error}</p>}

      <form onSubmit={onCreate} className="row task-form">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="新しいタスク"
          aria-label="新しいタスク"
        />
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as Priority)}
          aria-label="優先度"
        >
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          aria-label="期限"
        />
        <button type="submit">追加</button>
      </form>

      <div className="columns">
        {STATUSES.map((status) => {
          const columnTasks = tasks.filter((t) => t.status === status);
          return (
            <div key={status} className="column">
              <h3>
                {STATUS_LABEL[status]} <span className="count">{columnTasks.length}</span>
              </h3>
              {columnTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onMove={moveTask}
                  onDelete={onDelete}
                />
              ))}
            </div>
          );
        })}
      </div>
    </section>
  );
}

interface TaskCardProps {
  task: Task;
  onMove: (task: Task, status: Status) => void;
  onDelete: (id: string) => void;
}

function TaskCard({ task, onMove, onDelete }: TaskCardProps) {
  const index = STATUSES.indexOf(task.status);
  const prev = index > 0 ? STATUSES[index - 1] : null;
  const next = index < STATUSES.length - 1 ? STATUSES[index + 1] : null;

  return (
    <article className={`card priority-${task.priority}`}>
      <div className="card-title">{task.title}</div>
      <div className="card-meta">
        <span className={`badge badge-${task.priority}`}>{PRIORITY_LABEL[task.priority]}</span>
        {task.due_date && <span className="due">{task.due_date}</span>}
      </div>
      <div className="card-actions">
        <button
          disabled={!prev}
          onClick={() => prev && onMove(task, prev)}
          aria-label={`${task.title} を前の列へ`}
        >
          ←
        </button>
        <button
          disabled={!next}
          onClick={() => next && onMove(task, next)}
          aria-label={`${task.title} を次の列へ`}
        >
          →
        </button>
        <button
          className="link danger"
          onClick={() => onDelete(task.id)}
          aria-label={`${task.title} を削除`}
        >
          削除
        </button>
      </div>
    </article>
  );
}
