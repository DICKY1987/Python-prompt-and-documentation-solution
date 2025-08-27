#!/usr/bin/env python3
import re, sys, yaml, pandas as pd

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def search_token(text, token):
    import re
    return re.search(re.escape(token), text) is not None

def collect_ids_and_refs(checklist: dict):
    invariants = [item.get("id") for item in checklist.get("invariants", []) if item.get("id")]
    techniques = [item.get("id") for item in checklist.get("techniques", []) if item.get("id")]
    outputs = [item.get("id") for item in checklist.get("outputs", []) if item.get("id")]
    tests = []
    for t in checklist.get("tests", []):
        tests.append({
            "id": t.get("id"),
            "must_reference": t.get("must_reference", [])
        })
    return invariants, techniques, outputs, tests

def coverage_for_category(text, category_name, ids):
    present, missing = [], []
    for _id in ids:
        token = f"[{_id}]"
        (present if search_token(text, token) else missing).append(_id)
    total = len(ids)
    covered = len(present)
    ratio = covered / total if total else 1.0
    return {"category": category_name, "total": total, "present": covered, "coverage": ratio, "missing": missing, "present_ids": present}

def tests_coverage(text, tests):
    results = []
    for t in tests:
        tid = t.get("id")
        refs = t.get("must_reference", [])
        missing_refs = [ref for ref in refs if not search_token(text, ref)]
        passed = not missing_refs
        results.append({"test_id": tid, "must_reference": refs, "missing": missing_refs, "passed": passed})
    total = len(results)
    passes = sum(1 for r in results if r["passed"])
    ratio = passes / total if total else 1.0
    return results, {"category": "tests", "total": total, "present": passes, "coverage": ratio, "missing": [r["test_id"] for r in results if not r["passed"]]}

def main(spec_path, checklist_path, out_csv_path):
    text = load_text(spec_path)
    checklist = load_yaml(checklist_path)
    invariants, techniques, outputs, tests = collect_ids_and_refs(checklist)

    inv_cov = coverage_for_category(text, "invariants", invariants)
    tec_cov = coverage_for_category(text, "techniques", techniques)
    out_cov = coverage_for_category(text, "outputs", outputs)
    test_detail, test_cov = tests_coverage(text, tests)

    per_item_rows = []
    for cat, ids in [("invariants", invariants), ("techniques", techniques), ("outputs", outputs)]:
        for _id in ids:
            token = f"[{_id}]"
            per_item_rows.append({"category": cat, "id": _id, "found": search_token(text, token)})
    for tr in test_detail:
        per_item_rows.append({"category": "tests", "id": tr["test_id"], "found": tr["passed"]})

    summary_df = pd.DataFrame([inv_cov, tec_cov, out_cov, test_cov])
    per_item_df = pd.DataFrame(per_item_rows)
    tests_df = pd.DataFrame(test_detail)

    with open(out_csv_path, "w", encoding="utf-8") as f:
        f.write("# Summary\n")
        summary_df.to_csv(f, index=False)
        f.write("\n# Per-Item\n")
        per_item_df.to_csv(f, index=False)
        f.write("\n# Tests\n")
        tests_df.to_csv(f, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python prompt_coverage_checker.py <spec.md> <checklist.yaml> <out.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
