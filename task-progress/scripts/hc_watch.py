#!/usr/bin/env python3
"""Show a running hc terminal (e.g. fir/t18) as a card in the shared task-progress pane.
Usage: hc_watch.py <terminal> --title T [--desc D] [--on fir] [--probe 'remote sh snippet printing one status line'] [--every 15]
Text only (no bar) unless the probe line contains a tqdm-style 'NN%'. Finishes the card when the terminal exits."""
import argparse, json, os, re, subprocess, time

PP = os.path.expanduser("~/.claude/skills/task-progress/scripts/progress.py")
def pp(*a): subprocess.run(["python3", PP, *map(str, a)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def fmt(s): s = int(s); return f"{s//60}m{s%60:02d}s"

ap = argparse.ArgumentParser(); ap.add_argument("terminal"); ap.add_argument("--title", required=True); ap.add_argument("--desc", default="")
ap.add_argument("--on"); ap.add_argument("--probe"); ap.add_argument("--every", type=int, default=15); a = ap.parse_args()
f = f"/tmp/hcwatch-{a.terminal.replace('/', '_')}.json"
pp("init", f, "--title", a.title, "--desc", a.desc or f"terminal {a.terminal}"); pp("open", f)
t0 = time.time(); last_note = ""
while True:
    r = subprocess.run(["hc", "get", a.terminal], capture_output=True, text=True)
    try: d = json.loads(r.stdout)
    except ValueError: d = {}
    if d.get("state") == "finished" or not d:
        code = d.get("exit_code")
        (pp("done", f, "--msg", f"Finished in {fmt(time.time()-t0)}") if code in (0, None) and d
         else pp("fail", f, "--msg", f"Ended (exit {code}) after {fmt(time.time()-t0)}"))
        break
    note = ""
    if a.probe and a.on:
        p = subprocess.run(["hc", "run", "--on", a.on, "bash", "-c", a.probe], capture_output=True, text=True, timeout=90)
        note = " ".join(p.stdout.split())[:100]
    args = ["--step", f"Running {fmt(time.time()-t0)}" + (f" · {note}" if note else "")]
    m = re.search(r"(\d{1,3})%", note)
    if m: args += ["--percent", m[1]]
    if note and note != last_note: args += ["--log", note]; last_note = note
    pp("set", f, *args); time.sleep(a.every)
