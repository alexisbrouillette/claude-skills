#!/usr/bin/env python3
"""Usage limits for Claude Code and Antigravity as one JSON document (stdlib only).

  usage.py claude   -> {"ok", "plan", "rows": [{"label", "used", "resets_at"}], "error"?}
  usage.py agy      -> same shape, from `agy -p /usage` (free: a slash command, no model call)

`used` is percent used (0-100). `resets_at` is ISO-8601 UTC.
Claude: GET https://api.anthropic.com/api/oauth/usage with the Claude Code login in
~/.claude/.credentials.json (the same call Claude Code's /usage makes; token goes only to api.anthropic.com).
"""
import json, os, re, shutil, subprocess, sys, urllib.request

def claude():
    path = os.path.expanduser("~/.claude/.credentials.json")
    try: oauth = json.load(open(path))["claudeAiOauth"]
    except Exception as e: return {"ok": False, "error": f"no Claude Code login ({e.__class__.__name__})"}
    req = urllib.request.Request("https://api.anthropic.com/api/oauth/usage", headers={
        "Authorization": "Bearer " + oauth["accessToken"], "anthropic-beta": "oauth-2025-04-20",
        "User-Agent": "claude-code/herdr-usage"})
    try: d = json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": "login expired: open Claude Code once to refresh it" if e.code in (401, 403) else f"HTTP {e.code}"}
    except Exception as e: return {"ok": False, "error": str(e)}
    names = {"session": "5-hour", "weekly_all": "Weekly"}
    rows = []
    for l in d.get("limits") or []:
        label = names.get(l.get("kind")) or ("Weekly " + ((l.get("scope") or {}).get("model") or {}).get("display_name", l.get("kind", "?")))
        rows.append({"label": label, "used": l.get("percent") or 0, "resets_at": l.get("resets_at")})
    if not rows:  # older shape
        for key, label in (("five_hour", "5-hour"), ("seven_day", "Weekly"), ("seven_day_opus", "Weekly Opus"), ("seven_day_sonnet", "Weekly Sonnet")):
            if d.get(key): rows.append({"label": label, "used": d[key].get("utilization") or 0, "resets_at": d[key].get("resets_at")})
    return {"ok": True, "plan": oauth.get("subscriptionType"), "rows": rows}

def agy():
    exe = shutil.which("agy") or next((p for p in (os.path.expanduser("~/.gemini/bin/agy"), os.path.expanduser("~/.local/bin/agy"), "/usr/local/bin/agy") if os.access(p, os.X_OK)), None)
    if not exe: return {"ok": False, "error": "agy not installed"}
    try: r = subprocess.run([exe, "-p", "/usage"], capture_output=True, text=True, timeout=60)
    except Exception as e: return {"ok": False, "error": str(e)}
    rows = []
    for line in r.stdout.splitlines():
        c = [x.strip() for x in line.split("\t")]
        m = re.match(r"(\d+(?:\.\d+)?)%", c[2]) if len(c) >= 4 else None
        if not m: continue
        pool, kind = c[0], c[1]
        kind = re.sub(r"\s*Limit( Remaining)?", "", kind).replace(pool, "").strip()
        rows.append({"label": f"{pool} · {kind}" if kind else pool, "used": round(100 - float(m.group(1)), 1), "resets_at": c[3]})
    if not rows: return {"ok": False, "error": (r.stderr or r.stdout).strip()[:120] or "no usage output (signed in?)"}
    return {"ok": True, "rows": rows}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    if which not in ("claude", "agy"): sys.exit(__doc__)
    print(json.dumps(claude() if which == "claude" else agy()))
