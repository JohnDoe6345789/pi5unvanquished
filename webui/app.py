import os
import socket
from typing import Any, Dict, List
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

UNV_SERVER_HOST = os.environ.get("UNV_SERVER_HOST", "unvanq-server")
UNV_SERVER_PORT = int(os.environ.get("UNV_SERVER_PORT", "27960"))
STATUS_QUERY = b"\xff\xff\xff\xffgetstatus\n"

LOCALXPOSE_STATUS_URL = os.environ.get(
    "LOCALXPOSE_STATUS_URL",
    "http://unvanq-localxpose:4040/status",
)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
