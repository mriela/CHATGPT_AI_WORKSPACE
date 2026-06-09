#!/usr/bin/env python3
"""
ChatGPT Agent Bridge - Agent Loop v0.7
5秒ごとに tasks.json を監視し、タスクを処理するループランナー
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime

# agent_bridge ディレクトリを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(SCRIPT_DIR, "tasks.json")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "results.json")
STATUS_FILE = os.path.join(SCRIPT_DIR, "status.json")

# 監視間隔（秒）
POLL_INTERVAL = 5


def load_json(filepath):
    """JSONファイルを読み込む"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(filepath, data):
    """JSONファイルに保存する"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def process_create_file_task(task):
    """create_file タイプのタスクを処理する"""
    target = task.get("target")
    content = task.get("content", "")

    if not target:
        return False, "targetが指定されていません"

    # targetが相対パスの場合、agent_bridgeディレクトリ基準とする
    if not os.path.isabs(target):
        target_path = os.path.join(SCRIPT_DIR, target)
    else:
        target_path = target

    # 必要に応じて親ディレクトリを作成
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    # ファイルを作成
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True, f"{target} created"


def process_read_file_task(task):
    """read_file タイプのタスクを処理する"""
    target = task.get("target")

    if not target:
        return False, "targetが指定されていません", None

    # targetが相対パスの場合、agent_bridgeディレクトリ基準とする
    if not os.path.isabs(target):
        target_path = os.path.join(SCRIPT_DIR, target)
    else:
        target_path = target

    # ファイルが存在するか確認
    if not os.path.exists(target_path):
        return False, f"File not found: {target}", None

    # ファイルを読み込む
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        return True, f"{target} read", content
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None



def process_list_dir_task(task):
    """list_dir タイプのタスクを処理する"""
    target = task.get("target", SCRIPT_DIR)
    max_entries = int(task.get("max_entries", 200))

    if not os.path.isabs(target):
        target_path = os.path.join(SCRIPT_DIR, target)
    else:
        target_path = target

    if not os.path.isdir(target_path):
        return False, f"Directory not found: {target}", None

    hidden_names = {".git", "node_modules", "discord_bot_token.txt", ".env"}
    hidden_keywords = ["token", "secret", "password", "credential", "client_secret"]

    entries = []
    for name in os.listdir(target_path):
        lower_name = name.lower()

        if lower_name in hidden_names:
            continue
        if any(keyword in lower_name for keyword in hidden_keywords):
            continue

        full = os.path.join(target_path, name)
        st = os.stat(full)
        entries.append({
            "name": name,
            "path": full,
            "is_dir": os.path.isdir(full),
            "size": st.st_size,
            "last_write_time": datetime.fromtimestamp(st.st_mtime).isoformat()
        })

        if len(entries) >= max_entries:
            break

    return True, f"{target} listed", entries


def process_git_status_task(task):
    """git_status タイプのタスクを処理する"""
    repo = task.get("repo", SCRIPT_DIR)

    if not os.path.isabs(repo):
        repo_path = os.path.join(SCRIPT_DIR, repo)
    else:
        repo_path = repo

    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    output = result.stdout.strip()
    if result.stderr.strip():
        output += "\nSTDERR:\n" + result.stderr.strip()

    return result.returncode == 0, f"git status checked: {repo}", output

def process_tasks():
    """tasks.json からタスクを読み取り、処理する"""
    # 1. tasks.json を読む
    try:
        tasks_data = load_json(TASKS_FILE)
    except FileNotFoundError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] tasks.json が見つかりません")
        return False
    except json.JSONDecodeError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] tasks.json のJSON形式が無効です")
        return False

    tasks = tasks_data.get("tasks", [])

    if not tasks:
        return False  # タスクなし

    print(f"[{datetime.now().strftime('%H:%M:%S')}] found {len(tasks)} task(s)")

    # status.json を busy に更新
    status_data = load_json(STATUS_FILE)
    status_data["status"] = "busy"
    save_json(STATUS_FILE, status_data)

    # タスクを処理
    results = []
    for task in tasks:
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "")

        print(f"  Processing task: {task_id} (type: {task_type})")

        if task_type == "create_file":
            success, message = process_create_file_task(task)
            status = "completed" if success else "failed"
            result_entry = {
                "task_id": task_id,
                "status": status,
                "message": message
            }
        elif task_type == "read_file":
            success, message, file_content = process_read_file_task(task)
            status = "completed" if success else "failed"
            result_entry = {
                "task_id": task_id,
                "status": status,
                "message": message
            }
            if success and file_content is not None:
                result_entry["content"] = file_content
        elif task_type == "list_dir":
            success, message, entries = process_list_dir_task(task)
            status = "completed" if success else "failed"
            result_entry = {
                "task_id": task_id,
                "status": status,
                "message": message
            }
            if success and entries is not None:
                result_entry["entries"] = entries
        elif task_type == "git_status":
            success, message, output = process_git_status_task(task)
            status = "completed" if success else "failed"
            result_entry = {
                "task_id": task_id,
                "status": status,
                "message": message
            }
            if output is not None:
                result_entry["output"] = output
        else:
            success = False
            message = f"Unknown task type: {task_type}"
            status = "failed"
            result_entry = {
                "task_id": task_id,
                "status": status,
                "message": message
            }

        results.append(result_entry)

        print(f"    -> {status}: {message}")

    # results.json に completed を追加
    try:
        results_data = load_json(RESULTS_FILE)
    except (FileNotFoundError, json.JSONDecodeError):
        results_data = {"results": []}

    results_data["results"].extend(results)
    save_json(RESULTS_FILE, results_data)

    # tasks.json の tasks を空にする
    tasks_data["tasks"] = []
    save_json(TASKS_FILE, tasks_data)

    # status.json を idle に戻す
    status_data["status"] = "idle"
    save_json(STATUS_FILE, status_data)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(results)} task(s) processed.")
    return True


def run():
    """メインループ処理"""
    print("=" * 60)
    print("Agent Loop v0.7 開始...")
    print(f"Monitoring: {TASKS_FILE}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("Ctrl+C で終了します")
    print("=" * 60)

    try:
        while True:
            try:
                process_tasks()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")

            # 5秒待機
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("KeyboardInterrupt detected. Shutting down...")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    run()




