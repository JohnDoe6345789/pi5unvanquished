import http.server
import json
import os
import re
import signal
import subprocess
import threading
import time
from typing import Dict, List

status: Dict[str, object] = {
    "online": False,
    "public_url": None,
    "error": "",
    "process_exited": False,
    "pid": None,
}
_logs: List[str] = []
_proc: subprocess.Popen | None = None


def _append_log(line: str) -> None:
    _logs.append(line)
    if len(_logs) > 200:
        del _logs[: len(_logs) - 200]


def _run_loclx() -> None:
    global _proc

    token = os.environ.get("LOCALXPOSE_ACCESS_TOKEN")
    if not token:
        status["error"] = "LOCALXPOSE_ACCESS_TOKEN is not set"
        return

    to_addr = os.environ.get("LOCALXPOSE_TO", "unvanq-server:27960")
    region = os.environ.get("LOCALXPOSE_REGION", "")
    port = os.environ.get("LOCALXPOSE_PORT", "")
    reserved = os.environ.get("LOCALXPOSE_RESERVED_ENDPOINT", "")

    cmd = [
        "loclx",
        "tunnel",
        "--raw-mode",
        "udp",
        "--to",
        to_addr,
    ]

    if region:
        cmd.extend(["--region", region])
    if port:
        cmd.extend(["--port", port])
    if reserved:
        cmd.extend(["--reserved-endpoint", reserved])

    env = os.environ.copy()
    env["LOCALXPOSE_ACCESS_TOKEN"] = token
    # Newer LocalXpose builds expect ACCESS_TOKEN instead of LOCALXPOSE_ACCESS_TOKEN
    # so populate both to keep backward compatibility.
    env["ACCESS_TOKEN"] = token

    try:
        _proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
    except Exception as exc:
        status["error"] = f"Failed to start localxpose: {exc}"
        status["process_exited"] = True
        return

    status["pid"] = _proc.pid

    assert _proc.stdout is not None
    for raw in _proc.stdout:
        line = raw.rstrip("\n")
        if line:
            _append_log(line)

        match = re.search(r"udp://\S+", line)
        if match:
            status["public_url"] = match.group(0)
            status["online"] = True

        if not status["error"] and line.startswith("Error:"):
            status["error"] = line

    _proc.wait()
    status["process_exited"] = True
    if _proc.returncode not in (0, None) and not status["error"]:
        status["error"] = f"localxpose exited with code {_proc.returncode}"


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/status":
            payload = dict(status)
            payload["log_tail"] = list(_logs)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, *_: object) -> None:  # pragma: no cover
        return


def _shutdown() -> None:
    if _proc and _proc.poll() is None:
        try:
            _proc.terminate()
            _proc.wait(timeout=5)
        except Exception:
            try:
                _proc.kill()
            except Exception:
                pass


def main() -> None:
    worker = threading.Thread(target=_run_loclx, daemon=True)
    worker.start()

    port = int(os.environ.get("STATUS_PORT", "4040"))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)

    signal.signal(signal.SIGTERM, lambda *_: (_shutdown(), server.shutdown()))
    signal.signal(signal.SIGINT, lambda *_: (_shutdown(), server.shutdown()))

    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        _shutdown()
        worker.join(timeout=5)


if __name__ == "__main__":
    main()
