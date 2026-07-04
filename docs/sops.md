# sops

このリポジトリでは、共有 secret を sops + age で暗号化して管理します。

## インストール

```bash
mise install
```

プロジェクトの toolchain として `sops` と `age` を入れます。
mise の shim が `PATH` にない場合は、`mise x sops@latest -- ...` または
`mise x age@latest -- ...` 経由で実行してください。

## 初期鍵セットアップ

ローカルに age identity を作成します:

```bash
mkdir -p ~/.config/sops/age
mise x age@latest -- age-keygen -o ~/.config/sops/age/keys.txt
mise x age@latest -- age-keygen -y ~/.config/sops/age/keys.txt
```

表示された公開 recipient を `.sops.yaml` に設定します:

```yaml
creation_rules:
  - path_regex: apps/backend/\.env\.sops$
    age: age1...
```

`~/.config/sops/age/keys.txt` は秘密鍵です。リポジトリにコミットしないでください。

## バックエンド環境変数

共有するバックエンド secret ファイルを作成して暗号化します:

```bash
cp apps/backend/.env.sops.example apps/backend/.env.sops
$EDITOR apps/backend/.env.sops
mise x sops@latest -- sops --encrypt --in-place apps/backend/.env.sops
```

FastAPI が読むローカル `.env` へ復号します:

```bash
mise x sops@latest -- sops --decrypt apps/backend/.env.sops > apps/backend/.env
```

暗号化済みファイルを編集します:

```bash
mise x sops@latest -- sops apps/backend/.env.sops
```

コミット前に、ファイルが暗号化されていることを確認します:

```bash
mise x sops@latest -- sops --decrypt apps/backend/.env.sops >/dev/null
rg "ENC\\[" apps/backend/.env.sops
```
