#!/usr/bin/env python3
import re, sys, hashlib, json
from pathlib import Path

BASE = Path(".")
OUTPUTS = {
    "runtime_prompt": BASE / "Runtime_Prompt.md",
    "srs": BASE / "docs" / "out" / "SRS.md",
}
ID_PATTERN = re.compile(r"\[([A-Z]{2,4}-\d{3,})\]")

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

def scan_ids(txt: str):
    return sorted(set(ID_PATTERN.findall(txt)))

def make_fp():
    fp = {}
    for k, p in OUTPUTS.items():
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            fp[k] = {"file_hash": sha256_text(txt), "ids": scan_ids(txt)}
    return fp

def main():
    new_fp = make_fp()
    out = BASE / "sync_fingerprint.json"
    prev = {}
    if out.exists():
        try: prev = json.loads(out.read_text(encoding="utf-8"))
        except: prev = {}
    # Compare ID sets (vanishing IDs may indicate drops)
    problems = []
    for k in new_fp:
        new_ids = set(new_fp[k]["ids"])
        old_ids = set(prev.get(k, {}).get("ids", []))
        dropped = sorted(old_ids - new_ids)
        if dropped:
            problems.append(f"{k}: dropped IDs since last run -> {', '.join(dropped)}")
    out.write_text(json.dumps(new_fp, indent=2), encoding="utf-8")
    if problems:
        print("Sync fingerprint check found issues:")
        for p in problems: print("-", p)
        sys.exit(1)
    print("Sync fingerprint OK.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
