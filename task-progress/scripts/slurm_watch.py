#!/usr/bin/env python3
"""Show Slurm jobs of a machine (hc machine) as cards in the shared task-progress pane.
Usage: slurm_watch.py [--on fir] [--every 30]     (runs until killed; one instance per machine)
Percent only when the job log has a tqdm bar ("Ep 2/15: 40%|"); otherwise text only (state, elapsed of limit, last log line)."""
import argparse, os, re, subprocess, sys, time, json

PP = os.path.expanduser("~/.claude/skills/task-progress/scripts/progress.py")
REMOTE = r'''ids="$(squeue -u $(whoami) -h -o %i) $*"
for id in $(echo $ids | tr ' ' '\n' | sort -u); do
  row=$(sacct -j $id -n -X -P -o JobName,State,Elapsed,Timelimit,NodeList | head -1)
  out=$(scontrol show job $id 2>/dev/null | tr ' ' '\n' | grep '^StdOut=' | cut -d= -f2)
  last=""; [ -f "$out" ] && last=$(tail -c 800 "$out" | tr '\r' '\n' | tr -d '\000' | tail -n 1 | cut -c1-160)
  echo "$id|$row|$last"
done'''
EPOCH = re.compile(r"(?:Ep(?:och)?\s*)(\d+)\s*/\s*(\d+)")
PCT = re.compile(r"(\d{1,3})%\|")
RUNNING = {"RUNNING", "PENDING", "CONFIGURING", "COMPLETING", "SUSPENDED", "REQUEUED"}

def pp(*a): subprocess.run(["python3", PP, *map(str, a)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def percent(line):
    m, p = EPOCH.search(line), PCT.search(line)
    if m and p:
        ep, tot = int(m[1]), int(m[2])
        if 0 < ep <= tot: return round(((ep - 1) + int(p[1]) / 100) / tot * 100, 1)
    elif p: return int(p[1])
    return None

def clean(line): return re.sub(r"\s+", " ", line).strip()[:110]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--on", default="fir"); ap.add_argument("--every", type=int, default=30); a = ap.parse_args()
    pid = f"/tmp/slurm_watch_{a.on}.pid"
    try:
        if os.path.exists(pid): os.kill(int(open(pid).read()), 0); sys.exit(f"already running for {a.on}")
    except (ProcessLookupError, ValueError): pass
    open(pid, "w").write(str(os.getpid()))
    tracked, opened = {}, False          # id -> state file
    while True:
        r = subprocess.run(["hc", "run", "--on", a.on, "bash", "-c", REMOTE, "_", *[i for i, v in tracked.items() if not v["done"]]],
                           capture_output=True, text=True, timeout=120)
        for line in r.stdout.splitlines():
            p = line.split("|", 6)
            if len(p) < 7 or not p[0].isdigit() or not p[2]: continue
            jid, name, state, el, lim, node, last = p[0], p[1], p[2].split()[0], p[3], p[4], p[5], clean(p[6])
            t = tracked.get(jid)
            if t is None:
                f = f"/tmp/slurm-{a.on}-{jid}.json"
                if state not in RUNNING: continue          # ignore old finished jobs
                pp("init", f, "--title", f"{a.on} · {name} ({jid})", "--desc", f"time limit {lim}")
                if not opened: pp("open", f); opened = True
                else: pp("open", f)
                t = tracked[jid] = {"file": f, "done": False}
            if t["done"]: continue
            if state in RUNNING:
                step = f"{state.title()} · {el} of {lim}" + (f" · {node}" if node else "") + (f" · {last}" if last else "")
                pc = percent(last)
                pp("set", t["file"], "--step", step, *(["--percent", pc] if pc is not None else []))
            else:
                t["done"] = True
                (pp("done", t["file"], "--msg", f"{state} after {el}") if state == "COMPLETED"
                 else pp("fail", t["file"], "--msg", f"{state} after {el}"))
        time.sleep(a.every)
main()
