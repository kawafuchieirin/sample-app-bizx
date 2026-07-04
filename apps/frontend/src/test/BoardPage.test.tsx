import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../api/client";
import BoardPage from "../pages/BoardPage";
import type { Status, Task } from "../api/types";

vi.mock("../hooks/useToken", () => ({ useToken: () => "test-token" }));
vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  api: {
    listTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
  },
}));

const task = (over: Partial<Task> = {}): Task => ({
  id: "t1",
  board_id: "b1",
  title: "Write SPEC",
  description: "",
  status: "todo",
  priority: "high",
  due_date: null,
  created_at: "2026-07-04T00:00:00Z",
  updated_at: "2026-07-04T00:00:00Z",
  ...over,
});

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/boards/b1"]}>
      <Routes>
        <Route path="/boards/:boardId" element={<BoardPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("BoardPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders tasks grouped into status columns", async () => {
    vi.mocked(api.listTasks).mockResolvedValue([
      task(),
      task({ id: "t2", title: "Ship", status: "done" }),
    ]);
    renderPage();
    expect(await screen.findByText("Write SPEC")).toBeInTheDocument();
    expect(screen.getByText("Ship")).toBeInTheDocument();
    expect(api.listTasks).toHaveBeenCalledWith("test-token", "b1", { sort: "due" });
  });

  it("moves a task to the next status column", async () => {
    vi.mocked(api.listTasks).mockResolvedValue([task()]);
    vi.mocked(api.updateTask).mockImplementation((_t, _id, data) =>
      Promise.resolve(task({ status: data.status as Status })),
    );
    renderPage();
    await screen.findByText("Write SPEC");

    await userEvent.click(screen.getByRole("button", { name: "Write SPEC を次の列へ" }));

    await waitFor(() =>
      expect(api.updateTask).toHaveBeenCalledWith("test-token", "t1", { status: "in_progress" }),
    );
  });

  it("creates a task via the form", async () => {
    vi.mocked(api.listTasks).mockResolvedValue([]);
    vi.mocked(api.createTask).mockResolvedValue(task({ id: "t9", title: "New" }));
    renderPage();
    await screen.findByLabelText("新しいタスク");

    await userEvent.type(screen.getByLabelText("新しいタスク"), "New");
    await userEvent.click(screen.getByRole("button", { name: "追加" }));

    expect(api.createTask).toHaveBeenCalledWith("test-token", "b1", {
      title: "New",
      priority: "medium",
      due_date: null,
    });
    expect(await screen.findByText("New")).toBeInTheDocument();
  });
});
