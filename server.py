"""
Local API Server nhận dữ liệu đồng bộ từ FAP Chrome Extension / Tampermonkey.
Có thể chạy độc lập (`python server.py`) hoặc tự động khởi chạy ngầm bên trong `streamlit run app.py`.
"""

import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

DATA_DIR = Path(__file__).parent / "data"
PORT = 8000
_SERVER_STARTED = False
_LOCK = threading.Lock()
FLM_FILE = DATA_DIR / "flm_data.json"
_FLM_LOCK = threading.Lock()


def save_flm_page(payload: dict) -> dict:
    """Lưu bảng xuất từ FLM vào data/flm_data.json, mỗi trang một khóa (ghi đè khi xuất lại trang đó)."""
    page = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("page") or ""))[:80]
    headers, rows = payload.get("headers"), payload.get("rows")
    if not page:
        raise ValueError("Thiếu tên trang (page).")
    if not isinstance(headers, list) or not isinstance(rows, list) or not rows:
        raise ValueError("Dữ liệu bảng rỗng hoặc sai định dạng.")
    entry = {
        "source_url": str(payload.get("source_url") or "")[:500],
        "exported_at": str(payload.get("exported_at") or datetime.now(timezone.utc).isoformat()),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "headers": [str(h) for h in headers],
        "row_count": len(rows),
        "rows": rows,
    }
    with _FLM_LOCK:
        try:
            store = json.loads(FLM_FILE.read_text(encoding="utf-8")) if FLM_FILE.exists() else {}
            if not isinstance(store, dict):
                store = {}
        except Exception:
            store = {}
        if page == "syllabi":
            raise ValueError("Tên trang 'syllabi' dành riêng cho dữ liệu syllabus.")
        replaced = page in store
        store[page] = entry
        _write_flm_store(store)
    return {"page": page, "rows": len(rows), "replaced": replaced,
            "pages_in_file": sorted(k for k in store if k != "syllabi"), "file": str(FLM_FILE.name)}


def _write_flm_store(store: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA_DIR), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp, FLM_FILE)  # ghi nguyên tử, tránh hỏng file nếu bị ngắt giữa chừng


def save_flm_syllabus(payload: dict) -> dict:
    """Lưu một syllabus vào data/flm_data.json -> store['syllabi'][MÃ_MÔN]. Lưu lại cùng môn thì thay bản cũ;
    môn khác thì thêm vào, không ảnh hưởng các môn còn lại."""
    code = str(payload.get("subject_code") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,20}", code):
        raise ValueError(f"Mã môn không hợp lệ: {code!r}")
    key = code.upper()
    entry = {
        "subject_code": code,
        "source_url": str(payload.get("source_url") or "")[:500],
        "exported_at": str(payload.get("exported_at") or datetime.now(timezone.utc).isoformat()),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "info": payload.get("info") if isinstance(payload.get("info"), dict) else {},
    }
    for part in ("materials", "clos", "schedule", "questions", "assessments"):
        v = payload.get(part)
        entry[part] = v if isinstance(v, list) else []
    if not entry["assessments"] and not entry["info"]:
        raise ValueError("Syllabus rỗng (không có thông tin chung lẫn bảng đánh giá).")
    with _FLM_LOCK:
        try:
            store = json.loads(FLM_FILE.read_text(encoding="utf-8")) if FLM_FILE.exists() else {}
            if not isinstance(store, dict):
                store = {}
        except Exception:
            store = {}
        syl = store.get("syllabi")
        if not isinstance(syl, dict):
            syl = {}
        replaced = key in syl
        syl[key] = entry
        store["syllabi"] = syl
        _write_flm_store(store)
    return {"subject_code": code, "replaced": replaced, "subjects_in_file": len(syl), "file": str(FLM_FILE.name)}


class FAPSyncHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Giữ console gọn gàng khi chạy ngầm cùng Streamlit
        pass

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            resp = {"status": "ok", "service": "UniFs Chatbot FAP Receiver", "port": PORT}
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, code, obj):
        self.send_response(code)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        if self.path == "/api/v1/save-flm-syllabus":
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n > 5_000_000:
                    raise ValueError("Dữ liệu quá lớn (>5MB).")
                res = save_flm_syllabus(json.loads(self.rfile.read(n).decode("utf-8")))
                self._send_json(200, {"status": "success", **res})
                print(f"[UniFs Server] Đã lưu syllabus {res['subject_code']} -> data/{res['file']}")
            except Exception as e:
                self._send_json(400, {"status": "error", "message": str(e)})
            return
        if self.path == "/api/v1/save-flm-data":
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n > 5_000_000:
                    raise ValueError("Dữ liệu quá lớn (>5MB).")
                res = save_flm_page(json.loads(self.rfile.read(n).decode("utf-8")))
                self._send_json(200, {"status": "success", **res})
                print(f"[UniFs Server] Đã lưu FLM '{res['page']}' ({res['rows']} dòng) -> data/{res['file']}")
            except Exception as e:
                self._send_json(400, {"status": "error", "message": str(e)})
            return
        if self.path == "/api/v1/update-student-data":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                payload = json.loads(body.decode("utf-8"))
                student_id = (payload.get("student_id") or "UNKNOWN").strip().upper()
                transcript_records = payload.get("transcript") or []
                raw_attendance = payload.get("attendance") or []

                # Chuẩn hóa điểm danh từ DOM sang cấu trúc chuẩn của Advisor nếu cần
                if raw_attendance and isinstance(raw_attendance, list) and "subject_code" not in raw_attendance[0]:
                    total_s = len(raw_attendance)
                    absent_s = sum(1 for r in raw_attendance if any("absent" in str(x).lower() or "vắng" in str(x).lower() for x in r.get("data", [])))
                    attended_s = sum(1 for r in raw_attendance if any("present" in str(x).lower() or "có mặt" in str(x).lower() for x in r.get("data", [])))
                    max_abs = math.floor(max(total_s, 20) * 0.20)
                    rem_abs = max(max_abs - absent_s, 0)
                    is_af = absent_s > max_abs
                    payload["attendance"] = {
                        "student_id": student_id,
                        "subject_code": payload.get("current_subject") or "FAP-LIVE",
                        "subject_name": "Môn đồng bộ từ FAP",
                        "class_name": "FAP-SYNC",
                        "lecturer": "FAP Lecturer",
                        "total_slots": max(total_s, 20),
                        "current_slot": attended_s + absent_s,
                        "absent_slots": absent_s,
                        "attended_slots": attended_s,
                        "absent_rate_current": f"{round(100 * absent_s / max(attended_s + absent_s, 1), 1)}%",
                        "absent_rate_total": f"{round(100 * absent_s / max(total_s, 20), 1)}%",
                        "max_allowed_absent": max_abs,
                        "remaining_allowed_absent": rem_abs,
                        "is_attendance_fail": is_af,
                        "warning_status": "🚨 BỊ CẤM THI (AF)!" if is_af else f"✅ Đã vắng {absent_s}/{max(total_s, 20)} buổi (còn được phép vắng {rem_abs} buổi).",
                        "records": []
                    }

                # 1. Ghi trực tiếp vào SQL Database (SQLite / PostgreSQL)
                from database import upsert_fap_sync_to_db
                db_res = upsert_fap_sync_to_db(payload)

                # 2. Xóa cache của data_loader để chatbot nạp ngay dữ liệu mới từ Database
                try:
                    from data_loader import load_all
                    load_all.cache_clear()
                except Exception:
                    pass

                self.send_response(200)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()

                resp = {
                    "status": "success",
                    "message": f"Đã tự động đồng bộ dữ liệu FAP của SV {student_id} vào Database ({len(transcript_records)} môn)!",
                    "student_id": student_id,
                    "db_result": db_res
                }
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
                print(f"[UniFs Server] ✅ Auto-Sync thành công SV {student_id} vào Database.")

            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                err_resp = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(err_resp, ensure_ascii=False).encode("utf-8"))
                print(f"[UniFs Server] ❌ Lỗi xử lý: {e}")
        else:
            self.send_response(404)
            self.end_headers()


def is_port_in_use(port: int = PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_background_server() -> bool:
    """Khởi động FAP Sync Server chạy ngầm trong Daemon Thread (gọi tự động từ app.py)."""
    global _SERVER_STARTED
    with _LOCK:
        if _SERVER_STARTED or is_port_in_use(PORT):
            _SERVER_STARTED = True
            return True
        try:
            httpd = HTTPServer(("127.0.0.1", PORT), FAPSyncHandler)
            t = threading.Thread(target=httpd.serve_forever, daemon=True, name="FAPSyncServerThread")
            t.start()
            _SERVER_STARTED = True
            return True
        except Exception:
            return False


def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, FAPSyncHandler)
    print(f"🚀 UniFs Sync Server đang chạy tại: http://localhost:{PORT}")
    print(f"   API endpoint: http://localhost:{PORT}/api/v1/update-student-data")
    print("   Nhấn Ctrl + C để dừng server.")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()

