import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, ApiError } from "../api/client";
import type { Board } from "../api/types";
import { useToken } from "../hooks/useToken";

export default function BoardsPage() {
  const token = useToken();
  const [boards, setBoards] = useState<Board[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .listBoards(token)
      .then((data) => active && setBoards(data))
      .catch((e: ApiError) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [token]);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    try {
      const board = await api.createBoard(token, trimmed);
      setBoards((prev) => [...prev, board]);
      setName("");
    } catch (err) {
      setError((err as ApiError).message);
    }
  };

  const onDelete = async (id: string) => {
    try {
      await api.deleteBoard(token, id);
      setBoards((prev) => prev.filter((b) => b.id !== id));
    } catch (err) {
      setError((err as ApiError).message);
    }
  };

  if (loading) return <p className="center">読み込み中…</p>;

  return (
    <section className="boards">
      <h2>ボード</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onCreate} className="row">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="新しいボード名"
          aria-label="新しいボード名"
        />
        <button type="submit">作成</button>
      </form>
      <ul className="board-list">
        {boards.map((b) => (
          <li key={b.id}>
            <Link to={`/boards/${b.id}`}>{b.name}</Link>
            <button
              className="link danger"
              onClick={() => void onDelete(b.id)}
              aria-label={`${b.name} を削除`}
            >
              削除
            </button>
          </li>
        ))}
        {boards.length === 0 && <li className="muted">まだボードがありません。</li>}
      </ul>
    </section>
  );
}
