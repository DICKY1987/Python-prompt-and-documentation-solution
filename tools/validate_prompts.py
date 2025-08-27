#!/usr/bin/env python3
"""Validate prompt/config YAML files against a JSON Schema.

Usage:
  python tools/validate_prompts.py --schema prompt_schema_min.json [--root .]

- Finds YAML-like files commonly used in this repo (Prompt*.yaml, *manifest*.yaml, *rules*.yaml, *.yml).
- Validates each against the provided JSON schema.
- Prints a summary table and exits nonzero on any failure.

Requires: pyyaml, jsonschema
"""
from __future__ import annotations

import argparse
import json
import sys
import re
from pathlib import Path
from typing import List, Tuple

import yaml  # type: ignore
from jsonschema import Draft202012Validator, exceptions as jsonschema_exceptions  # type: ignore


PATTERNS = [
    r"""^Prompt.*\.ya?ml$""",
    r""".*manifest.*\.ya?ml$""",
    r""".*rules.*\.ya?ml$""",
    r""".*config.*\.ya?ml$""",
    r""".*\.ya?ml$""",  # fallback catch-all
]


def discover_yaml_files(root: Path) -> List[Path]:
    candidates: List[Path] = []
    for p in root.rglob("*.yaml"):
        candidates.append(p)
    for p in root.rglob("*.yml"):
        candidates.append(p)
    # simple priority ordering: earlier patterns first
    def priority(path: Path) -> Tuple[int, str]:
        name = str(path.as_posix())
        for i, pat in enumerate(PATTERNS):
            if re.search(pat, name, re.IGNORECASE):
                return (i, name)
        return (len(PATTERNS), name)
    return sorted(set(candidates), key=priority)


def load_schema(schema_path: Path):
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_one(validator, path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        return False, [f"YAML parse error: {e}"]
    try:
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
            loc = "/".join(map(str, err.path)) or "<root>"
            errors.append(f"{path}: {loc}: {err.message}")
    except jsonschema_exceptions.SchemaError as e:
        return False, [f"Schema error: {e}"]
    return len(errors) == 0, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, help="Path to JSON schema file (e.g., prompt_schema_min.json)")
    ap.add_argument("--root", default=".", help="Root directory to scan (default: .)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    schema_path = Path(args.schema).resolve()

    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}", file=sys.stderr)
        return 2

    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)

    files = discover_yaml_files(root)
    if not files:
        print("No YAML files found. Nothing to validate.")
        return 0

    total = 0
    passed = 0
    failed = 0
    failures: List[str] = []

    print(f"Validating {len(files)} YAML files against schema: {schema_path.name}\n")
    for fp in files:
        total += 1
        ok, errors = validate_one(validator, fp)
        if ok:
            print(f"✔ PASS: {fp}")
            passed += 1
        else:
            print(f"✖ FAIL: {fp}")
            for e in errors:
                print(f"    • {e}")
            failed += 1
            failures.extend(errors)

    print("\nSummary:")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
