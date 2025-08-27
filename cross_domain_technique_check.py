#!/usr/bin/env python3
import sys, yaml, json, re
from pathlib import Path

BASE = Path(".")
PSPEC = BASE / "PromptSpec.yaml"
TECS = BASE / "docs" / "sources" / "techniques.yaml"
SRS = BASE / "docs" / "out" / "SRS.md"

def load_yaml(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    # If no PromptSpec, nothing to verify
    if not PSPEC.exists():
        print("[SKIP] PromptSpec.yaml not found; cross-domain technique check skipped.")
        return 0
    if not TECS.exists():
        print("[FAIL] docs/sources/techniques.yaml missing.")
        return 1

    ps = load_yaml(PSPEC) or {}
    req_tecs = (ps.get("meta", {}) or {}).get("required_techniques", [])
    if not req_tecs:
        print("[OK] No required_techniques specified in PromptSpec.meta; nothing to verify.")
        return 0

    tec_items = (load_yaml(TECS) or {}).get("items", [])
    tec_ids = {t.get("id") for t in tec_items if t.get("id")}
    missing = [t for t in req_tecs if t not in tec_ids]
    if missing:
        print("Missing technique references in docs/sources/techniques.yaml for:", ", ".join(missing))
        return 1

    # Ensure compiled docs mention each technique ID (e.g., via the Techniques table)
    if SRS.exists():
        srs_txt = SRS.read_text(encoding="utf-8")
        absent = [t for t in req_tecs if t not in srs_txt]
        if absent:
            print("Compiled SRS does not include technique IDs:", ", ".join(absent))
            return 1
        print("[OK] All required techniques are documented and present in SRS.")
    else:
        print("[WARN] SRS not found; cannot verify presence in compiled docs.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
