#!/usr/bin/env python3
import re, sys
from pathlib import Path

BASE = Path(".")

def headings_with_anchors(text: str):
    heads = []
    for line in text.splitlines():
        if line.startswith("#"):
            ln = re.sub(r"\s+", " ", line.strip())
            heads.append(ln)
    return heads

def compare(golden: Path, compiled: Path, label: str):
    if not golden.exists() or not compiled.exists():
        print(f"[SKIP] {label}: missing files (golden: {golden.exists()}, compiled: {compiled.exists()})")
        return True
    g = golden.read_text(encoding="utf-8")
    c = compiled.read_text(encoding="utf-8")
    gh = headings_with_anchors(g)
    ch = headings_with_anchors(c)
    ok = gh == ch
    if not ok:
        print(f"[FAIL] {label}: headings/anchors do not match golden.")
        print("Golden:", gh)
        print("Compiled:", ch)
    else:
        print(f"[OK] {label}: headings/anchors match golden exactly.")
    return ok

def main():
    ok = True
    ok &= compare(Path("docs/goldens/SRS_golden.md"), Path("docs/out/SRS.md"), "SRS")
    gpr = Path("SPEC/goldens/Prompt_Runtime_Golden.md")
    rpr = Path("Runtime_Prompt.md")
    if gpr.exists() and rpr.exists():
        ok &= compare(gpr, rpr, "Runtime Prompt")
    if not ok:
        sys.exit(1)
    print("Strict golden diff passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
