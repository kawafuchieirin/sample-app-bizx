# コントリビューションガイド

はじめての方も歓迎です！このプロジェクトへの参加手順をやさしくまとめました。
はじめてなら [docs/onboarding.md](docs/onboarding.md)（全体像・用語集）も先に読むとスムーズです。

## 1. 準備

必要なツール（`mise` があればまとめて入ります）:

```bash
# 1) このリポジトリを取得
git clone https://github.com/kawafuchieirin/sample-app-bizx.git
cd sample-app-bizx

# 2) 必要ツールが揃っているか確認
make doctor

# 3) ツールチェーンと依存をまとめてセットアップ
make setup
```

`make doctor` で「必須ツール」に ✗ が出たら、[docs/onboarding.md](docs/onboarding.md) の導入手順を参照してください。

## 2. ローカルで動かす

まずは動かして体感するのがおすすめです。

```bash
make test          # まず全テストが通ることを確認
make dev-frontend  # フロントを起動 → http://localhost:5173
```

アプリの動作確認は、デプロイ済みの AWS バックエンドを使う「方式A」が最速です。
詳しくは [docs/deploy.md](docs/deploy.md) のローカル手順を参照。

## 3. 変更を加える流れ

`main` に直接コミットせず、**ブランチ → PR** で進めます。

```bash
# 1) ブランチを作る（種別/内容 の形式）
git switch -c feat/add-task-labels

# 2) コードを変更

# 3) 出す前に自動チェック（CIと同じ内容）
make check        # lint + typecheck + test

# 4) コミット（下記の規約に従う）
git add -A
git commit -m "feat: タスクにラベルを追加"

# 5) プッシュして PR を作成
git push -u origin feat/add-task-labels
gh pr create   # または GitHub の画面から
```

PR を作ると自動で CI（lint・型・テスト）が走ります。緑になっていれば OK です。

## 4. ルール（かんたん）

### ブランチ名
`種別/内容` の形式。種別は下のコミット種別と同じ。
例: `feat/board-sort`, `fix/login-redirect`, `docs/readme`

### コミットメッセージ（Conventional Commits・日本語で）
`種別: 変更内容` の1行。

| 種別 | 使うとき |
|---|---|
| `feat` | 機能追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメント |
| `test` | テスト |
| `refactor` | 挙動を変えないリファクタ |
| `chore` | 雑務・設定・依存更新 |

例: `fix: 期限未設定のタスクが並び替えで先頭に来る不具合を修正`

### コードスタイル
手で整える必要はありません。自動整形・チェックに任せます。

```bash
make format     # 整形（ruff）
make lint       # 静的チェック（ruff / eslint）
make typecheck  # 型チェック（mypy / tsc）
```

### テスト
- 変更した振る舞いには**テストを足す**のが基本です
- バックエンドは `apps/backend/tests/`（pytest + moto）、フロントは `apps/frontend/src/test/`（vitest）
- 既存テストを参考にするのが近道です

## 5. こんなときは

- **何から手を付ければ？** → Issue の `good first issue` ラベルがおすすめ
- **用語がわからない** → [docs/onboarding.md](docs/onboarding.md) の用語集
- **セットアップで詰まった** → `make doctor` の結果と一緒に Issue を立ててください
- **仕様を知りたい** → [SPEC.md](SPEC.md)

小さな修正（誤字・コメント追加）でも大歓迎です。気軽にどうぞ！
