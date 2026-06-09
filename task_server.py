#!/usr/bin/env python3
"""
Task Server - HTTPサーバー経由で tasks.json にタスクを追加する
localhost:8765 で待受し、POST /task エンドポイントを提供する

OpenAPI schema に準拠:
- Bearer Token 認証（TASK_SERVER_API_KEY 環境変数）
- POST /task - タスク追加（認証必要）
- GET /health - ヘルスチェック（認証不要）
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# agent_bridge ディレクトリへのパス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(SCRIPT_DIR, "agent_bridge", "tasks.json")

# サーバー設定
HOST = "localhost"
PORT = 8765

# 認証設定
API_KEY = os.environ.get("TASK_SERVER_API_KEY", "")
AUTH_REQUIRED = API_KEY != ""  # API_KEY が設定されていれば認証必須


class TaskHandler(BaseHTTPRequestHandler):
    """POST /task リクエストを処理するハンドラー"""

    def _check_auth(self):
        """Bearer Token 認証をチェックする"""
        if not AUTH_REQUIRED:
            return True, None  # 認証が設定されていない場合はスキップ

        auth_header = self.headers.get("Authorization", "")
        print(f"[DEBUG] Authorization header: {auth_header[:20]}..." if len(auth_header) > 20 else f"[DEBUG] Authorization header: {auth_header}")
        print(f"[DEBUG] API_KEY (first 5 chars): {API_KEY[:5]}..." if len(API_KEY) > 5 else f"[DEBUG] API_KEY: {API_KEY}")

        if not auth_header.startswith("Bearer "):
            print(f"[DEBUG] Auth failed: Missing 'Bearer ' prefix")
            return False, "Missing or invalid Authorization header. Use: Bearer <token>"

        token = auth_header[7:]  # "Bearer " の7文字を除去
        print(f"[DEBUG] Extracted token (first 5 chars): {token[:5]}..." if len(token) > 5 else f"[DEBUG] Extracted token: {token}")

        if token != API_KEY:
            print(f"[DEBUG] Auth failed: Token mismatch")
            return False, "Invalid API key"

        print(f"[DEBUG] Auth success!")
        return True, None

    def do_POST(self):
        """POST リクエストを処理する"""
        if self.path != "/task":
            self.send_error(404, "Not Found")
            return

        # 認証チェック
        is_authenticated, error_message = self._check_auth()
        if not is_authenticated:
            self._send_json_response(401, "error", error_message)
            return

        # Content-Length を取得
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json_response(400, "error", "Request body is empty")
            return

        # リクエストボディを読み込む
        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json_response(400, "error", "Invalid JSON format")
            return
        except Exception as e:
            self._send_json_response(500, "error", f"Failed to read request: {str(e)}")
            return

        # tasks.json に追記する
        success, message = self._append_task(data)
        if success:
            self._send_json_response(200, "success", message)
        else:
            self._send_json_response(500, "error", message)

    def do_GET(self):
        """GET リクエストを処理する（ヘルスチェック用）"""
        if self.path == "/health":
            # ヘルスチェックは認証不要
            self._send_json_response(200, "ok", "Server is running")
        elif self.path == "/":
            self._send_json_response(200, "ok", "Task Server is running. POST /task to add tasks.")
        else:
            self.send_error(404, "Not Found")

    def _send_json_response(self, status_code, status, message, data=None):
        """JSON レスポンスを送信する"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        response = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if data is not None:
            response["data"] = data

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))

    def _append_task(self, new_task):
        """tasks.json に新しいタスクを追記する"""
        try:
            # 既存の tasks.json を読み込む
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
            else:
                tasks_data = {"tasks": []}

            # tasks リストが存在することを確認
            if "tasks" not in tasks_data:
                tasks_data["tasks"] = []

            # 新しいタスクがリストの場合と単体の場合を処理
            if isinstance(new_task, list):
                tasks_data["tasks"].extend(new_task)
                added_count = len(new_task)
            else:
                tasks_data["tasks"].append(new_task)
                added_count = 1

            # tasks.json に保存
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)

            return True, f"{added_count} task(s) added to tasks.json"

        except FileNotFoundError:
            return False, f"Tasks file not found: {TASKS_FILE}"
        except json.JSONDecodeError:
            return False, "Invalid JSON in tasks.json"
        except Exception as e:
            return False, f"Failed to update tasks.json: {str(e)}"

    def log_message(self, format, *args):
        """ログメッセージをカスタマイズする"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


def run_server():
    """HTTP サーバーを起動する"""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, TaskHandler)

    print("=" * 60)
    print("Task Server 開始...")
    print(f"Listening on http://{HOST}:{PORT}")
    print(f"POST /task - タスクを追加")
    print(f"GET /health - ヘルスチェック")
    print(f"Tasks file: {TASKS_FILE}")
    print("Ctrl+C で終了します")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("KeyboardInterrupt detected. Shutting down...")
        print("=" * 60)
        httpd.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    run_server()