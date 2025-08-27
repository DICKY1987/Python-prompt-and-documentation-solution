#!/usr/bin/env python3
import json
from pathlib import Path

def color_for(pct):
    if pct >= 95:
        return "green"
    if pct >= 80:
        return "yellow"
    return "red"

def write_badge(path, label, pct):
    msg = f"{pct:.0f}%"
    data = {"schemaVersion": 1, "label": label, "message": msg, "color": color_for(pct)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    print(f"Wrote {path} -> {msg}")

def main():
    src = Path("badges_prompt_status.json")
    if not src.exists():
        # Write N/A badges
        for name, label in [
            ("prompt_invariants.json","invariants"),
            ("prompt_techniques.json","techniques"),
            ("prompt_outputs.json","outputs"),
            ("prompt_tests.json","tests"),
        ]:
            (Path("badges")/name).write_text(json.dumps({"schemaVersion":1,"label":label,"message":"n/a","color":"lightgrey"}), encoding="utf-8")
        print("badges_prompt_status.json not found; wrote default badges.")
        return 0

    j = json.loads(src.read_text(encoding="utf-8"))
    cov = j.get("coverage", {})
    def pct(key):
        v = cov.get(key, 0)
        try:
            return float(v)*100 if v <= 1 else float(v)
        except Exception:
            return 0.0

    write_badge(Path("badges/prompt_invariants.json"), "invariants", pct("invariants"))
    write_badge(Path("badges/prompt_techniques.json"), "techniques", pct("techniques"))
    write_badge(Path("badges/prompt_outputs.json"), "outputs", pct("outputs"))
    write_badge(Path("badges/prompt_tests.json"), "tests", pct("tests"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
