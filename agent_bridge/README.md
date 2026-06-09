# ChatGPT Agent Bridge v0.9

AIエージェント（Cline）とタスク管理システムを連携させるためのブリッジシステムです。

## 概要

tasks.json にタスクを追加するだけで、agent_loop.py が自動的にタスクを処理し、results.json に結果を記録します。

## サポートされているタスクタイプ

### 1. create_file
ファイルを新規作成します。

```json
{
  "id": "task001",
  "type": "create_file",
  "target": "hello.txt",
  "content": "Hello from Task"
}
```

### 2. read_file
ファイルの内容を読み取り、results.json に記録します。

```json
{
  "id": "task002",
  "type": "read_file",
  "target": "hello.txt"
}
```

**結果例:**
```json
{
  "task_id": "task002",
  "status": "completed",
  "message": "hello.txt read",
  "content": "Hello from Task"
}
```

## 使い方

### agent_loop.py の起動（常駐モード）

```bash
cd agent_bridge
python agent_loop.py
```

- 5秒ごとに tasks.json を監視
- タスクがあれば自動処理
- Ctrl+C で終了

### 既知の注意点

1. **agent_loop.py の再起動が必要な場合があります**
   - コードを変更した後、古いプロセスが残っていると新機能が反映されません
   - その場合は一度 Ctrl+C で停止し、再起動してください

2. **現在はまだ人間中継あり**
   - 完全自動化には至っておらず、一部人間の操作が必要です

## ファイル構成

| ファイル | 説明 |
|----------|------|
| `agent_loop.py` | 常駐タスクループ（v0.7〜） |
| `agent_runner.py` | 単発タスクランナー（旧） |
| `tasks.json` | 未処理タスクキュー |
| `results.json` | 完了タスク結果 |
| `status.json` | エージェント状態（idle/busy） |