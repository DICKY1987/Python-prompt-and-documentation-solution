#!/usr/bin/env python3
import json, sys, yaml
from pathlib import Path
from jsonschema import validate, Draft202012Validator

BASE = Path(".")
SCHEMAS = BASE / "SPEC" / "schemas"

def load_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def load_yaml(p): return yaml.safe_load(Path(p).read_text(encoding="utf-8"))

def must_schema(name):
    sp = SCHEMAS / name
    if not sp.exists():
        print(f"[SCHEMA MISSING] {name}", file=sys.stderr)
        sys.exit(1)
    s = load_json(sp)
    Draft202012Validator.check_schema(s)
    return s

def main():
    errs = 0

    # PromptSpec.yaml
    if (BASE / "PromptSpec.yaml").exists():
        sch = must_schema("prompt_spec.schema.json")
        inst = load_yaml(BASE / "PromptSpec.yaml")
        try:
            validate(inst, sch); print("[OK] PromptSpec.yaml")
        except Exception as e:
            print(f"[FAIL] PromptSpec.yaml: {e}"); errs += 1

    # Prompt checklist (try a few filenames)
    chk = None
    for cand in ["Prompt_Checklist_v1.0.yaml", "Prompt_Checklist.yaml"]:
        p = BASE / cand
        if p.exists():
            chk = p; break
    if chk:
        sch = must_schema("prompt_checklist.schema.json")
        inst = load_yaml(chk)
        try:
            validate(inst, sch); print(f"[OK] {chk.name}")
        except Exception as e:
            print(f"[FAIL] {chk.name}: {e}"); errs += 1

    # Prompt sync manifest (sync_manifest.yaml or prompt/prompt_sync_manifest.yaml)
    man = None
    for cand in ["sync_manifest.yaml", "prompt/prompt_sync_manifest.yaml"]:
        p = BASE / cand
        if p.exists():
            man = p; break
    if man:
        sch = must_schema("prompt_sync_manifest.schema.json")
        inst = load_yaml(man)
        try:
            validate(inst, sch); print(f"[OK] {man.as_posix()}")
        except Exception as e:
            print(f"[FAIL] {man.as_posix()}: {e}"); errs += 1

    # Docs: registry & manifest
    reg = BASE / "docs" / "registry.yaml"
    if reg.exists():
        sch = must_schema("doc_registry.schema.json")
        inst = load_yaml(reg)
        try:
            validate(inst, sch); print("[OK] docs/registry.yaml")
        except Exception as e:
            print(f"[FAIL] docs/registry.yaml: {e}"); errs += 1

    dman = BASE / "doc_manifest.yaml"
    if dman.exists():
        sch = must_schema("doc_manifest.schema.json")
        inst = load_yaml(dman)
        try:
            validate(inst, sch); print("[OK] doc_manifest.yaml")
        except Exception as e:
            print(f"[FAIL] doc_manifest.yaml: {e}"); errs += 1

    if errs:
        print(f"Validation failed with {errs} error(s).")
        sys.exit(1)
    print("Live config validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
