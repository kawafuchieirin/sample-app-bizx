import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../api/client";
import BoardsPage from "../pages/BoardsPage";
import type { Board } from "../api/types";

vi.mock("../hooks/useToken", () => ({ useToken: () => "test-token" }));
vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  api: {
    listBoards: vi.fn(),
    createBoard: vi.fn(),
    deleteBoard: vi.fn(),
  },
}));

const board = (over: Partial<Board> = {}): Board => ({
  id: "b1",
  name: "Work",
  created_at: "2026-07-04T00:00:00Z",
  updated_at: "2026-07-04T00:00:00Z",
  ...over,
});

function renderPage() {
  return render(
    <MemoryRouter>
      <BoardsPage />
    </MemoryRouter>,
  );
}

describe("BoardsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("lists boards from the API", async () => {
    vi.mocked(api.listBoards).mockResolvedValue([board()]);
    renderPage();
    expect(await screen.findByText("Work")).toBeInTheDocument();
  });

  it("shows an empty state when there are no boards", async () => {
    vi.mocked(api.listBoards).mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText("まだボードがありません。")).toBeInTheDocument();
  });

  it("creates a board and appends it to the list", async () => {
    vi.mocked(api.listBoards).mockResolvedValue([]);
    vi.mocked(api.createBoard).mockResolvedValue(board({ id: "b2", name: "Home" }));
    renderPage();
    await screen.findByText("まだボードがありません。");

    await userEvent.type(screen.getByLabelText("新しいボード名"), "Home");
    await userEvent.click(screen.getByRole("button", { name: "作成" }));

    expect(api.createBoard).toHaveBeenCalledWith("test-token", "Home");
    expect(await screen.findByText("Home")).toBeInTheDocument();
  });

  it("deletes a board", async () => {
    vi.mocked(api.listBoards).mockResolvedValue([board()]);
    vi.mocked(api.deleteBoard).mockResolvedValue();
    renderPage();
    await screen.findByText("Work");

    await userEvent.click(screen.getByRole("button", { name: "Work を削除" }));

    await waitFor(() => expect(api.deleteBoard).toHaveBeenCalledWith("test-token", "b1"));
    expect(screen.queryByText("Work")).not.toBeInTheDocument();
  });
});
