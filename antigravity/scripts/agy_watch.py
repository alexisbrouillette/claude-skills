#!/usr/bin/env python3
"""Run agy with a live progress pane (task-progress skill). Text steps only: no bar, since agy gives no real percentage.
Usage: agy_watch.py <model> "<prompt>" [--title T] [--out FILE]
Env: AGY_CWD, AGY_MODE (default plan), AGY_SETTINGS (session-only allow-list JSON). Final answer goes to stdout and --out."""
import json, os, subprocess, sys, tempfile, time, shutil, argparse

PP = ["python3", os.path.expanduser("~/.claude/skills/task-progress/scripts/progress.py")]
def pp(*a): subprocess.run(PP + list(a), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_agy():
    for c in (shutil.which("agy"), *(os.path.expanduser(p) for p in ("~/.gemini/bin/agy", "~/.local/bin/agy")), "/usr/local/bin/agy"):
        if c and os.access(c, os.X_OK): return c
    sys.exit("agy not found")

def clip(s, n=90): s = " ".join(str(s).split()); return s if len(s) <= n else s[:n-1] + "…"

def describe(name, params):
    p = params or {}
    if name == "run_command": return "Running: " + clip(p.get("CommandLine", ""))
    path = next((p[k] for k in ("AbsolutePath", "FilePath", "Path", "File", "TargetFile", "SearchPath", "Query", "Pattern") if k in p), "")
    verb = {"view_file": "Reading", "read_file": "Reading", "list_dir": "Listing", "grep_search": "Searching", "find_by_name": "Finding", "write_to_file": "Writing", "replace_file_content": "Editing"}.get(name, f"Using {name}")
    return clip(f"{verb} {path}".strip())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("prompt")
    ap.add_argument("--title", default="Antigravity"); ap.add_argument("--out"); a = ap.parse_args()
    f = os.path.join(tempfile.gettempdir(), f"progress-agy-{os.getpid()}.json")
    pp("init", f, "--title", a.title, "--desc", f"agy · {a.model}"); pp("open", f)
    cmd = [find_agy(), "-p", a.prompt, "--model", a.model, "--mode", os.environ.get("AGY_MODE", "plan"), "--output-format", "stream-json"]
    if os.environ.get("AGY_SETTINGS"): cmd += ["--settings", os.environ["AGY_SETTINGS"]]
    pp("set", f, "--step", "Starting agent…")
    proc = subprocess.Popen(cmd, cwd=os.environ.get("AGY_CWD") or None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    answer, last, steps, writing, t0, last_set = [], "", 0, False, time.time(), 0
    for line in proc.stdout:
        try: ev = json.loads(line)
        except ValueError: continue
        u = ev.get("step_update") or {}
        if u.get("step_type") == "tool":
            ti = u.get("tool_info") or {}; txt = describe(u.get("tool_name", ""), ti.get("parameters"))
            if u.get("state") == "ACTIVE" and txt != last:
                last = txt; steps += 1; pp("set", f, "--step", txt)
            elif u.get("state") == "DONE": pp("set", f, "--log", txt)
        elif u.get("step_type") == "agent_response" and u.get("text_delta") is not None:
            answer.append(u["text_delta"])
            if not writing: writing = True; pp("set", f, "--step", "Writing the answer…")
            elif time.time() - last_set > 3: last_set = time.time(); pp("set", f, "--step", f"Writing the answer… ({sum(map(len, answer))} chars)")
        elif u.get("state") == "ACTIVE" and u.get("step_type") not in ("user_input", "tool", "agent_response") and not writing:
            pp("set", f, "--step", "Thinking…")
    err = proc.stderr.read(); rc = proc.wait(); out = "".join(answer).strip()
    if rc == 0 and out:
        pp("done", f, "--msg", f"Finished in {int(time.time()-t0)}s, {steps} tool steps")
        if a.out: open(a.out, "w").write(out + "\n")
        print(out)
    else:
        msg = clip(err.strip().splitlines()[-1] if err.strip() else "agy returned no answer", 120)
        pp("fail", f, "--msg", msg); print(err or "agy returned no answer", file=sys.stderr)
        if a.out: open(a.out, "w").write(err or "no answer\n")
        sys.exit(rc or 1)
main()
