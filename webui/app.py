import json
import os
import socket
from pathlib import Path
from typing import Any, Dict, List
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

UNV_SERVER_HOST = os.environ.get("UNV_SERVER_HOST", "unvanq-server")
UNV_SERVER_PORT = int(os.environ.get("UNV_SERVER_PORT", "27960"))
STATUS_QUERY = b"\xff\xff\xff\xffgetstatus\n"

LOCALXPOSE_STATUS_URL = os.environ.get(
    "LOCALXPOSE_STATUS_URL",
    "http://unvanq-localxpose:4040/status",
)

PANEL_ORDER_FILE = Path(os.environ.get("PANEL_ORDER_FILE", "/data/panel_order.json"))
DEFAULT_PANEL_ORDER = ["server", "localxpose"]
ALLOWED_PANELS = set(DEFAULT_PANEL_ORDER)


def normalize_panel_order(order: List[str]) -> List[str]:
    """Remove unknown/duplicate panel ids and ensure defaults are present."""
    cleaned: List[str] = []
    for item in order:
        if isinstance(item, str) and item in ALLOWED_PANELS and item not in cleaned:
            cleaned.append(item)
    for default in DEFAULT_PANEL_ORDER:
        if default not in cleaned:
            cleaned.append(default)
    return cleaned


def load_panel_order() -> List[str]:
    if not PANEL_ORDER_FILE.exists():
        return DEFAULT_PANEL_ORDER

    try:
        with PANEL_ORDER_FILE.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        if isinstance(data, list):
            return normalize_panel_order(data)
    except Exception:
        pass
    return DEFAULT_PANEL_ORDER


def save_panel_order(order: List[str]) -> None:
    PANEL_ORDER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PANEL_ORDER_FILE.open("w", encoding="utf-8") as fp:
        json.dump(order, fp)

# ----------------------------------------------------
# Unvanquished Server Query
# ----------------------------------------------------
def query_unvanquished_server() -> Dict[str, Any]:
    result = {
        "online": False,
        "info": {},
        "players": [],
        "raw": "",
        "error": "",
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.5)

    try:
        sock.sendto(STATUS_QUERY, (UNV_SERVER_HOST, UNV_SERVER_PORT))
        data, _ = sock.recvfrom(65535)
    except Exception as exc:
        result["error"] = str(exc)
        return result
    finally:
        sock.close()

    try:
        text = data.decode("latin-1", errors="replace")
    except:
        text = repr(data)

    result["raw"] = text
    lines = text.split("\n")

    if len(lines) < 2:
        result["error"] = "Unexpected response"
        return result

    info = parse_info_string(lines[1])
    players = [
        parse_player_line(l)
        for l in lines[2:]
        if l.strip()
    ]
    players = [p for p in players if p]

    result["online"] = True
    result["info"] = info
    result["players"] = players

    return result


def parse_info_string(info: str) -> Dict[str, str]:
    parts = info.split("\\")
    if parts and parts[0] == "":
        parts = parts[1:]

    out = {}
    it = iter(parts)
    for k in it:
        try:
            out[k] = next(it)
        except StopIteration:
            break
    return out


def parse_player_line(line: str):
    parts = line.strip().split(" ", 2)
    if len(parts) < 3:
        return None

    try:
        score = int(parts[0])
    except:
        score = 0
    try:
        ping = int(parts[1])
    except:
        ping = 0

    rest = parts[2]
    name = rest
    if "\"" in rest:
        a = rest.find("\"") + 1
        b = rest.rfind("\"")
        if b > a:
            name = rest[a:b]

    return {"score": score, "ping": ping, "name": name}


# ----------------------------------------------------
# LocalXpose Tunnel Query
# ----------------------------------------------------
def query_localxpose_status() -> Dict[str, Any]:
    result = {
        "online": False,
        "public_url": None,
        "error": "",
        "log_tail": [],
    }

    try:
        r = requests.get(LOCALXPOSE_STATUS_URL, timeout=1.0)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["log_tail"] = data.get("log_tail", [])
    result["public_url"] = data.get("public_url")
    result["online"] = bool(data.get("online") and result["public_url"])
    if not result["error"]:
        result["error"] = data.get("error", "") or ""

    return result


@app.route("/")
def index():
    return render_template("index.j2")

@app.route("/api/status")
def api_status():
    return jsonify(query_unvanquished_server())

@app.route("/api/localxpose_status")
def api_localxpose():
    return jsonify(query_localxpose_status())

@app.route("/api/panel_order", methods=["GET", "POST"])
def api_panel_order():
    if request.method == "GET":
        return jsonify({"order": load_panel_order()})

    body = request.get_json(silent=True) or {}
    requested = body.get("order")
    if not isinstance(requested, list):
        return jsonify({"error": "order must be a list"}), 400

    normalized = normalize_panel_order(requested)
    try:
        save_panel_order(normalized)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"order": normalized})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
