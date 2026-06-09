# ChatGPT Agent Bridge 運用ルール v0.9

## 概要
ChatGPT Agent Bridgeは、AIエージェント（Cline）とタスク管理システムを連携させるためのブリッジシステムです。

## ファイル構成

### 1. README.md
- プロジェクトの説明文書
- 内容: "ChatGPT Agent Bridge"

### 2. status.json
- エージェントの現在状態を管理
- 構造:
  ```json
  {
    "agent": "cline",
    "status": "idle"
  }
  ```
- 状態値: `idle`, `busy`, `error`

### 3. tasks.json
- 未完了タスクのキューを管理
- 構造:
  ```json
  {
    "tasks": []
  }
  ```
- 各タスクはタスクID、内容、優先度などを含む

### 4. results.json
- 完了したタスクの結果を保存
- 構造:
  ```json
  {
    "results": []
  }
  ```
- 各結果はタスクID、成否、出力などを含む

## 運用フロー

1. **タスク追加**: tasks.json に新しいタスクを追加
2. **状態確認**: status.json でエージェントの状態を確認
3. **タスク実行**: agent_loop.py が tasks.json からタスクを自動取得して実行（5秒間隔）
4. **結果保存**: 完了したタスクの結果を results.json に保存
5. **状態更新**: status.json の状態を更新

## サポートされているタスクタイプ

### create_file
ファイルを作成します。

```json
{
  "id": "task001",
  "type": "create_file",
  "target": "hello.txt",
  "content": "Hello from Task"
}
```

### read_file
ファイルを読み取り、results.json の content フィールドに内容を記録します。

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

## Task → Agent → Result の流れ

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Task        │────▶│     Agent       │────▶│     Result      │
│                 │     │                 │     │                 │
│ tasks.json      │     │ status.json     │     │ results.json    │
│ task_example    │     │ (idle→busy)     │     │ result_example  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Task**: task_example.json などのタスクが tasks.json に追加される
2. **Agent**: エージェントがタスクを取得し、status.json を idle→busy に変更して処理を実行
3. **Result**: 処理完了後、result_example.json のような結果を results.json に保存し、status.json を idle に戻す

## タスクの具体例

### task_example.json
task_example.json には、ファイル作成タスクの例が記載されています。

```json
{
  "id": "task001",
  "type": "create_file",
  "target": "agent_bridge/hello.txt",
  "content": "Hello from Task"
}
```

**task_example.json を Agent が処理した場合、hello.txt が生成されます。**

## 注意事項
- 各JSONファイルは常に有効なJSON形式を維持してください
- 同時に複数のプロセスがファイルにアクセスする場合は、排他制御を考慮してください
- エラー発生時は status.json の status を "error" に設定してください

## 既知の注意点

1. **agent_loop.py の再起動が必要な場合があります**
   - コードを変更した後、古いプロセスが残っていると新機能が反映されません
   - その場合は一度 Ctrl+C で停止し、再起動してください

2. **現在はまだ人間中継あり**
   - 完全自動化には至っておらず、一部人間の操作が必要です

## 変更履歴

| バージョン | 日付 | 内容 |
|-----------|------|------|
| v0.6 | - | agent_loop.py 作成（5秒監視ループ） |
| v0.7 | - | read_file タスクタイプ追加 |
| v0.9 | - | README.md/PROTOCOL.md 更新、create_file/read_file 成功 |
