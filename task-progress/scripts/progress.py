#!/usr/bin/env python3
"""Live progress viewer for long-running tasks. Stdlib only.

  progress.py init  FILE --title T [--desc D] [--steps N]
  progress.py set   FILE [--percent P] [--step "what is happening"] [--log "line"] [--title T] [--desc D]
  progress.py done  FILE [--msg M]      progress.py fail FILE [--msg M]
  progress.py watch FILE                (the live view; Ctrl-C to close)
  progress.py open  FILE                (launch `watch` in a new terminal window)
  progress.py demo                      (simulated task, runs the view in this terminal)
"""
import argparse, json, os, shlex, shutil, subprocess, sys, tempfile, time

def load(f):
    try:
        with open(f) as fh: return json.load(fh)
    except Exception: return {}

def save(f, d):
    tmp = f + ".tmp"
    with open(tmp, "w") as fh: json.dump(d, fh)
    os.replace(tmp, f)

def cmd_init(a):
    save(a.file, {"title": a.title, "desc": a.desc or "", "percent": None, "step": "Starting…",
                  "log": [], "status": "running", "start": time.time(), "end": None, "msg": ""})

def cmd_set(a):
    d = load(a.file)
    if a.title: d["title"] = a.title
    if a.desc is not None: d["desc"] = a.desc
    if a.percent is not None: d["percent"] = max(0, min(100, a.percent))
    if a.step: d["step"] = a.step
    if a.log: d.setdefault("log", []).append([time.time(), a.log]); d["log"] = d["log"][-30:]
    save(a.file, d)

def finish(a, status):
    d = load(a.file); d["status"] = status; d["end"] = time.time(); d["msg"] = a.msg or ""
    if status == "done": d["percent"] = 100
    save(a.file, d)

# ---------- rendering ----------
R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
def fg(n): return f"\033[38;5;{n}m"
GRAD = [39, 38, 44, 43, 49, 48, 84, 83]   # cyan -> green
SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

def fmt(s):
    s = int(s); h, r = divmod(s, 3600); m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def bar(width, pct, t, status):
    if pct is None:   # indeterminate: sliding block
        w = max(6, width // 6); pos = int((t * 18) % (width + w)) - w
        cells = [("█" if pos <= i < pos + w else "░") for i in range(width)]
        return "".join(fg(GRAD[min(len(GRAD)-1, i * len(GRAD) // width)]) + c if c == "█" else DIM + fg(240) + c
                       for i, c in enumerate(cells)) + R
    filled = width * pct / 100; full = int(filled); out = ""
    for i in range(width):
        if i < full: out += fg(82 if status == "done" else GRAD[min(len(GRAD)-1, i * len(GRAD) // width)]) + "█"
        elif i == full and filled - full >= 0.5: out += fg(GRAD[min(len(GRAD)-1, i * len(GRAD) // width)]) + "▌"
        else: out += fg(238) + "░"
    return out + R

def clip(s, n): return s if len(s) <= n else s[: max(0, n - 1)] + "…"

def render(d, t):
    cols, rows = shutil.get_terminal_size((80, 24)); w = min(cols - 4, 76); pad = "  "
    status = d.get("status", "running"); pct = d.get("percent")
    start = d.get("start") or t; end = d.get("end") or t; el = end - start
    if status == "done": icon, col = "✔", fg(82)
    elif status == "failed": icon, col = "✘", fg(203)
    else: icon, col = SPIN[int(t * 10) % len(SPIN)], fg(45)
    L = [""]
    L.append(f"{pad}{col}{B}{icon}  {clip(d.get('title','Task'), w-4)}{R}")
    if d.get("desc"): L.append(f"{pad}{DIM}{clip(d['desc'], w)}{R}")
    L.append("")
    label = "…" if pct is None else f"{pct:>3.0f}%"
    L.append(f"{pad}{bar(w - 6, pct, t, status)} {B}{label}{R}")
    meta = f"elapsed {fmt(el)}"
    if status == "running" and pct and pct >= 3: meta += f"  ·  ~{fmt(el * (100 - pct) / pct)} left"
    L.append(f"{pad}{DIM}{meta}{R}")
    L.append("")
    if status == "running": L.append(f"{pad}{B}▸ {clip(d.get('step',''), w-2)}{R}")
    else:
        msg = d.get("msg") or ("Completed" if status == "done" else "Failed")
        L.append(f"{pad}{col}{B}{clip(msg, w)}{R}")
    log = d.get("log", [])[-max(0, min(6, rows - len(L) - 3)):]
    if log:
        L.append("")
        for ts, line in log:
            L.append(f"{pad}{DIM}{time.strftime('%H:%M:%S', time.localtime(ts))}  {clip(line, w-10)}{R}")
    return "\n".join(L)

def cmd_watch(a):
    sys.stdout.write("\033[?1049h\033[?25l"); last = None
    try:
        while True:
            d = load(a.file); t = time.time()
            frame = render(d, t) if d else "\n  Waiting for task…"
            sys.stdout.write("\033[H" + frame.replace("\n", "\033[K\n") + "\033[K\033[J"); sys.stdout.flush()
            if d.get("status") in ("done", "failed") and last is None: last = t
            if last and t - last > 1.5:
                sys.stdout.write(f"\n  {DIM}Press Ctrl-C to close.{R}"); sys.stdout.flush()
                while True: time.sleep(3600)
            time.sleep(0.1)
    except KeyboardInterrupt: pass
    finally: sys.stdout.write("\033[?25h\033[?1049l"); sys.stdout.flush()

def cmd_open(a):
    me = os.path.abspath(__file__); inner = f"python3 {shlex.quote(me)} watch {shlex.quote(os.path.abspath(a.file))}"
    for term, args in (("gnome-terminal", ["--title=Task progress", "--geometry=84x16", "--", "bash", "-c", inner]),
                       ("kitty", ["bash", "-c", inner]), ("alacritty", ["-e", "bash", "-c", inner]),
                       ("konsole", ["-e", "bash", "-c", inner]), ("xterm", ["-e", "bash", "-c", inner])):
        if shutil.which(term):
            subprocess.Popen([term] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            print(f"opened in {term}"); return
    print("No GUI terminal found. Ask the user to run in a terminal:\n  " + inner)

def cmd_demo(a):
    f = os.path.join(tempfile.mkdtemp(), "demo.json"); me = os.path.abspath(__file__)
    script = f'''
import subprocess, time
P = ["python3", {me!r}]
def s(*x): subprocess.run(P + list(x))
s("init", {f!r}, "--title", "Rebuilding the indicator dataset", "--desc", "Demo: simulated long-running task")
steps = [("Downloading raw data", 0, 25, ["Fetched 12 tiles", "Fetched 48 tiles", "Download complete"]),
         ("Reprojecting rasters", 25, 55, ["Reprojected EPSG:4326 → 32198", "Clipped to study area"]),
         ("Computing indicators", 55, 90, ["Habitat destruction: ok", "Carbon sink: ok", "Connectivity: ok"]),
         ("Writing outputs", 90, 100, ["Wrote 9 GeoTIFFs"])]
for name, a, b, logs in steps:
    s("set", {f!r}, "--step", name, "--percent", str(a)); n = 12
    for i in range(1, n + 1):
        time.sleep(0.25); s("set", {f!r}, "--percent", str(a + (b - a) * i // n))
        if i % 4 == 0 and logs: s("set", {f!r}, "--log", logs.pop(0))
s("done", {f!r}, "--msg", "All 9 indicators rebuilt")
'''
    subprocess.Popen([sys.executable, "-c", script]); a.file = f; cmd_watch(a)

p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
for name in ("init", "set", "done", "fail", "watch", "open"):
    sp = sub.add_parser(name); sp.add_argument("file")
    if name == "init": sp.add_argument("--title", required=True); sp.add_argument("--desc"); sp.add_argument("--steps")
    if name == "set":
        sp.add_argument("--percent", type=float); sp.add_argument("--step"); sp.add_argument("--log")
        sp.add_argument("--title"); sp.add_argument("--desc")
    if name in ("done", "fail"): sp.add_argument("--msg")
sub.add_parser("demo")
a = p.parse_args()
{"init": cmd_init, "set": cmd_set, "done": lambda a: finish(a, "done"), "fail": lambda a: finish(a, "failed"),
 "watch": cmd_watch, "open": cmd_open, "demo": cmd_demo}[a.cmd](a)
