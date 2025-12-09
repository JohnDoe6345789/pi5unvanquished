import os
import socket
from typing import Any, Dict, List
import requests
from flask import Flask, jsonify, render_template_string

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


# ----------------------------------------------------
# Embedded React + Material UI Page
# ----------------------------------------------------

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>Unvanquished Pi-5 Dashboard</title>

<link rel="stylesheet"
 href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"/>
<link rel="stylesheet"
 href="https://fonts.googleapis.com/icon?family=Material+Icons"/>

<script crossorigin="anonymous"
 integrity="sha384-DGyLxAyjq0f9SPpVevD6IgztCFlnMF6oW/XQGmfe+IsZ8TqEiDrcHkMLKI6fiB/Z"
 src="https://unpkg.com/react@18.3.1/umd/react.production.min.js"></script>
<script crossorigin="anonymous"
 integrity="sha384-gTGxhz21lVGYNMcdJOyq01Edg0jhn/c22nsx0kyqP0TxaV5WVdsSH1fSDUf5YJj1"
 src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
<script crossorigin="anonymous"
 integrity="sha384-gfoIoghgrQ+acOP1IAci7PIH0wjwxDVkjgSczIHAcAGEWKu6Ztq1HaNa41oW95ya"
 src="https://unpkg.com/@babel/standalone@7.26.0/babel.min.js"></script>

<script crossorigin="anonymous"
 integrity="sha384-C1jZRQpcgcAFclz/eCOntp9Rs1moYZ1axTf9rL7aS3DQMSW3XESRolQKVUey9T3C"
 src="https://unpkg.com/@mui/material@5.15.14/umd/material-ui.production.min.js"></script>

<script>
window.API_STATUS_URL = "/api/status";
window.API_LOCALXPOSE_URL = "/api/localxpose_status";
</script>

</head>
<body style="margin:0;background:#000;">
<div id="root"></div>

<script type="text/babel">

const {
  Box, Typography, Chip, Card, CardHeader, CardContent,
  Button, Stack, Table, TableHead, TableRow, TableCell,
  TableBody, ThemeProvider, createTheme, CssBaseline, Container
} = MaterialUI;

function useServerData() {
  const [status, setStatus] = React.useState({loading:true, error:"", data:null});
  const [lx, setLx] = React.useState({loading:true, error:"", data:null});

  React.useEffect(() => {
    let dead = false;

    async function tick() {
      try {
        const r = await fetch(window.API_STATUS_URL);
        const j = await r.json();
        if (!dead) setStatus({loading:false,error:"",data:j});
      } catch(e) {
        if (!dead) setStatus(p => ({loading:false,error:String(e),data:p.data}));
      }

      try {
        const r = await fetch(window.API_LOCALXPOSE_URL);
        const j = await r.json();
        if (!dead) setLx({loading:false,error:"",data:j});
      } catch(e) {
        if (!dead) setLx(p => ({loading:false,error:String(e),data:p.data}));
      }
    }

    tick();
    const id = setInterval(tick, 5000);
    return () => { dead = true; clearInterval(id); };
  }, []);

  return {status, lx};
}

function StatusChip({label, online}) {
  return (
    <Chip
      label={label + ": " + (online ? "Online" : "Offline")}
      color={online ? "success" : "error"}
      size="small"
      variant={online ? "filled" : "outlined"}
    />
  );
}

function App() {
  const {status, lx} = useServerData();

  const serverOnline = !!(status.data && status.data.online);
  const info = (status.data && status.data.info) || {};
  const players = (status.data && status.data.players) || [];

  const lxData = lx.data || {};
  const lxOnline = !!lxData.online;
  const lxUrl = lxData.public_url || "N/A";

  const theme = createTheme({
    palette: {
      mode: "dark",
      primary: { main: "#4caf50" }
    }
  });

  const copyLocalxpose = () => {
    if (lxOnline && lxUrl !== "N/A")
      navigator.clipboard.writeText(lxUrl);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline/>
      <Box sx={{py:4, bgcolor:"#000", minHeight:"100vh"}}>
        <Container maxWidth="md">

          <Typography variant="h4" gutterBottom>
            Unvanquished Pi-5 Server Dashboard
          </Typography>

          <Stack direction="row" spacing={1} sx={{mb:2}}>
            <Chip label="React" variant="outlined"/>
            <Chip label="Material UI" variant="outlined"/>
            <Chip label="Flask" variant="outlined"/>
            <Chip label="Docker" variant="outlined"/>
          </Stack>

          <Stack spacing={2}>

            <Card>
              <CardHeader
                title="Game Server"
                action={<StatusChip label="Server" online={serverOnline}/>}
              />
              <CardContent>
                {status.loading ? (
                  <Typography>Loading…</Typography>
                ) : (
                <>
                  <Box sx={{
                    display:"grid",
                    gridTemplateColumns:"repeat(auto-fit, minmax(140px,1fr))",
                    gap:1, mb:1
                  }}>
                    <Box>
                      <Typography variant="caption">Hostname</Typography>
                      <Typography>{info.sv_hostname || "N/A"}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Map</Typography>
                      <Typography>{info.mapname || "N/A"}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Game</Typography>
                      <Typography>{info.gamename || "N/A"}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Players</Typography>
                      <Typography>{players.length}</Typography>
                    </Box>
                  </Box>

                  {players.length > 0 && (
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>#</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Score</TableCell>
                          <TableCell>Ping</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {players.map((p,i) => (
                          <TableRow key={i}>
                            <TableCell>{i+1}</TableCell>
                            <TableCell>{p.name}</TableCell>
                            <TableCell>{p.score}</TableCell>
                            <TableCell>{p.ping}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader
                title="LocalXpose Tunnel"
                action={<StatusChip label="LocalXpose" online={lxOnline}/>}
              />
              <CardContent>
                <Typography variant="caption">Public UDP URL</Typography>
                <Typography sx={{wordBreak:"break-all", mb:1}}>
                  {lxUrl}
                </Typography>

                <Stack direction="row" spacing={1}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    onClick={copyLocalxpose}
                    disabled={!lxOnline}
                  >
                    Copy LocalXpose Address
                  </Button>
                </Stack>

                {lx.error && (
                  <Typography variant="caption" color="warning.main">
                    Error: {lx.error}
                  </Typography>
                )}
              </CardContent>
            </Card>

          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
</script>

</body>
</html>
"""

# ----------------------------------------------------
# Routes
# ----------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/status")
def api_status():
    return jsonify(query_unvanquished_server())

@app.route("/api/localxpose_status")
def api_localxpose():
    return jsonify(query_localxpose_status())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
