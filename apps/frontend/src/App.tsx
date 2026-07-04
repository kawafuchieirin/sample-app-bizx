import { useAuth } from "react-oidc-context";
import { Link, Navigate, Route, Routes } from "react-router-dom";

import { cognitoLogoutUrl } from "./auth/oidc";
import BoardPage from "./pages/BoardPage";
import BoardsPage from "./pages/BoardsPage";

export default function App() {
  const auth = useAuth();

  if (auth.isLoading) {
    return <div className="center">読み込み中…</div>;
  }

  if (auth.error) {
    return <div className="center error">認証エラー: {auth.error.message}</div>;
  }

  if (!auth.isAuthenticated) {
    return (
      <div className="center login">
        <h1>bizx タスク管理</h1>
        <p>ログインして始めましょう。</p>
        <button onClick={() => void auth.signinRedirect()}>ログイン</button>
      </div>
    );
  }

  const email = auth.user?.profile.email ?? "";
  const signOut = () => {
    void auth.removeUser();
    window.location.href = cognitoLogoutUrl();
  };

  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">
          bizx
        </Link>
        <div className="spacer" />
        <span className="email">{email}</span>
        <button className="link" onClick={signOut}>
          ログアウト
        </button>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<BoardsPage />} />
          <Route path="/boards/:boardId" element={<BoardPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
