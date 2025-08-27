#!/usr/bin/env python3
import re, sys, yaml, json
from pathlib import Path

BASE = Path(".")
ID_PATTERN = re.compile(r"\[([A-Z]{2,4}-\d{3,})\]")
ALLOWED_PREFIXES = {"REQ","ADR","TST","GLO","SEC","OBJ","PRC","ROL","INP","OUT","GRD","REF","CHG","TEC","INV"}

def load_yaml(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def gather_defined_ids() -> set:
    ids = set()
    # Docs sources
    for p in [
        BASE / "docs" / "sources" / "requirements.yaml",
        BASE / "docs" / "sources" / "tests.yaml",
        BASE / "docs" / "sources" / "glossary.yaml",
    ]:
        if p.exists():
            data = load_yaml(p) or {}
            for item in (data.get("items") or []):
                if "id" in item: ids.add(item["id"])
    # ADR dir
    adr_dir = BASE / "docs" / "sources" / "adrs"
    if adr_dir.exists():
        for p in adr_dir.glob("*.yaml"):
            data = load_yaml(p) or {}
            for item in (data.get("items") or []):
                if "id" in item: ids.add(item["id"])
    # Prompt checklist IDs (INV/TEC/OUT/TST-like)
    for p in [BASE / "Prompt_Checklist_v1.0.yaml", BASE / "Prompt_Checklist.yaml"]:
        if p.exists():
            data = load_yaml(p) or {}
            for k in ["invariants","techniques","outputs","tests"]:
                for item in (data.get(k) or []):
                    if "id" in item: ids.add(item["id"])
    return ids

def scan_ids_in_file(p: Path) -> set:
    txt = p.read_text(encoding="utf-8")
    return set(ID_PATTERN.findall(txt))

def main():
    defined = gather_defined_ids()
    # Scan compiled outputs
    files = []
    rp = BASE / "Runtime_Prompt.md"
    if rp.exists(): files.append(rp)
    srs = BASE / "docs" / "out" / "SRS.md"
    if srs.exists(): files.append(srs)
    missing = {}
    extraneous = set()
    dupes = set() # duplicates across definitions are caught by set but we can add logic if needed

    # Ensure all bracket-IDs in outputs resolve to defined or allowed pseudo prefixes
    for f in files:
        seen = scan_ids_in_file(f)
        for sid in seen:
            pref = sid.split("-")[0]
            if pref not in ALLOWED_PREFIXES and sid not in defined:
                missing.setdefault(f.as_posix(), []).append(sid)
            elif (pref in {"REQ","ADR","TST","GLO","TEC","INV"} and sid not in defined):
                missing.setdefault(f.as_posix(), []).append(sid)

    # Check for duplicates in defined set by counting across sources
    # (Simple approach: collect all and ensure unique. Real dup detection would need source mapping.)
    # Here we just pass, because set eliminates dupes; you can extend to map provenance.

    if missing:
        print("Unresolved IDs found in compiled artifacts:")
        for fn, ids in missing.items():
            print(f"- {fn}: {sorted(set(ids))}")
        sys.exit(1)

    print("ID integrity OK (all bracketed IDs resolve to known or allowed prefixes).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
