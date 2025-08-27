#!/usr/bin/env python3
"""
SPEC/tools/validate_spec.py
Validates JSON Schemas in SPEC/schemas and example instances in SPEC/examples.
"""
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, validate

BASE = Path(__file__).resolve().parents[1]
SCHEMAS = BASE / "schemas"
EXAMPLES = BASE / "examples"

def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # Load schemas
    schema_files = sorted(SCHEMAS.glob("*.json"))
    schemas = {}
    for s in schema_files:
        try:
            data = load_json(s)
            Draft202012Validator.check_schema(data)  # raises if invalid
            schemas[s.name] = data
        except Exception as e:
            print(f"[SCHEMA ERROR] {s.name}: {e}")
            sys.exit(1)
    print(f"Loaded {len(schemas)} schemas OK.")

    # Validate examples (schema chosen by filename prefix)
    example_files = sorted(EXAMPLES.glob("*.json"))
    failures = 0
    for ex in example_files:
        data = load_json(ex)
        # Pick schema by convention
        # prompt_spec_min.json -> prompt_spec.schema.json, etc.
        stem = ex.stem.replace("_min","").replace("_example","")
        schema_name = stem + ".schema.json"
        sch = schemas.get(schema_name)
        if not sch:
            print(f"[WARN] No schema found for example {ex.name} (looked for {schema_name})")
            continue
        try:
            validate(instance=data, schema=sch)
            print(f"[OK] {ex.name} validated against {schema_name}")
        except Exception as e:
            print(f"[FAIL] {ex.name} -> {schema_name}: {e}")
            failures += 1

    if failures:
        print(f"Validation failed with {failures} error(s).")
        sys.exit(1)
    print("SPEC validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
