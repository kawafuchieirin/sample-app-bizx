import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

const useAuthMock = vi.fn();
vi.mock("react-oidc-context", () => ({
  useAuth: () => useAuthMock(),
}));

function renderApp() {
  return render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
}

describe("App", () => {
  beforeEach(() => useAuthMock.mockReset());

  it("shows a loading state while auth initializes", () => {
    useAuthMock.mockReturnValue({ isLoading: true });
    renderApp();
    expect(screen.getByText("読み込み中…")).toBeInTheDocument();
  });

  it("shows a login button when unauthenticated", () => {
    useAuthMock.mockReturnValue({ isLoading: false, isAuthenticated: false });
    renderApp();
    expect(screen.getByRole("button", { name: "ログイン" })).toBeInTheDocument();
  });

  it("surfaces auth errors", () => {
    useAuthMock.mockReturnValue({ isLoading: false, error: new Error("boom") });
    renderApp();
    expect(screen.getByText(/認証エラー: boom/)).toBeInTheDocument();
  });
});
