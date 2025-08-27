
#!/usr/bin/env python3
import os, sys, time, json, yaml, hashlib, subprocess, pandas as pd, re
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def load_manifest(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def write_text(path: Path, content: str):
    path.write_text(content, encoding="utf-8")

def calc_coverage(spec_text: str, checklist: dict):
    def find_token(tok): return re.search(re.escape(tok), spec_text) is not None
    def cov_for(ids, wrap=True):
        present = []
        missing = []
        for _id in ids:
            tok = f"[{_id}]" if wrap else _id
            (present if find_token(tok) else missing).append(_id)
        total = len(ids); covered = len(present); ratio = (covered/total) if total else 1.0
        return {"total": total, "present": covered, "coverage": ratio, "present_ids": present, "missing": missing}
    inv_ids = [x.get("id") for x in checklist.get("invariants",[]) if x.get("id")]
    tec_ids = [x.get("id") for x in checklist.get("techniques",[]) if x.get("id")]
    out_ids = [x.get("id") for x in checklist.get("outputs",[]) if x.get("id")]
    # Tests reference literal tokens like "[OUT-SRS-001]"
    tests = []
    for t in checklist.get("tests", []):
        missing = [ref for ref in t.get("must_reference", []) if not find_token(ref)]
        tests.append({"id": t.get("id"), "missing": missing, "passed": len(missing)==0})
    test_cov = {"total": len(tests), "present": sum(1 for t in tests if t["passed"]), "coverage": (sum(1 for t in tests if t["passed"]) / len(tests)) if tests else 1.0}
    return {
        "invariants": cov_for(inv_ids),
        "techniques": cov_for(tec_ids),
        "outputs": cov_for(out_ids),
        "tests": test_cov,
        "tests_detail": tests
    }

def structural_checks(prompt_path: Path, rules: dict):
    text = read_text(prompt_path)
    issues = []
    if rules.get("max_chars") and len(text) > rules["max_chars"]:
        issues.append(f"Prompt too long (> {rules['max_chars']} chars): {len(text)}")
    for b in rules.get("banned_phrases", []):
        if b in text.lower():
            issues.append(f"Banned phrase: {b}")
    return {"len": len(text), "issues": issues}

def main(argv):
    CI = ("--ci" in argv) or ("--check" in argv)
    base = Path(".")
    manifest = load_manifest(base / "sync_manifest.yaml")
    paths = manifest["paths"]
    spec = base / paths["spec"]
    checklist = base / paths["checklist"]
    patches = [base / p for p in paths.get("patches", []) if p]
    compiler = base / paths["compiler"]
    runtime = base / paths["runtime_prompt"]
    sync_report = base / paths["sync_report"]
    lockfile = base / paths["lockfile"]
    badge_json = base / paths["badge_json"]
    structural_rules = manifest.get("structural", {})
    coverage_threshold = manifest.get("coverage_threshold", 0.95)

    # Compute input hashes
    input_files = [spec, checklist, *patches]
    inputs_hash = {str(p): sha256_file(p) for p in input_files if p.exists()}
    lock = {}
    if lockfile.exists():
        try:
            lock = json.loads(lockfile.read_text(encoding="utf-8"))
        except Exception:
            lock = {}

    changed = (inputs_hash != lock.get("inputs_hash"))
    # Always rebuild if runtime missing
    if not runtime.exists():
        changed = True

    # Step 1: Compile
    if changed:
        cmd = [sys.executable, str(compiler), str(spec), patches[0].as_posix() if patches else "none", str(runtime)]
        subprocess.run(cmd, check=True)

    # Step 2: Coverage calc
    spec_text = read_text(runtime)
    with open(checklist, "r", encoding="utf-8") as f:
        chk = yaml.safe_load(f)
    coverage = calc_coverage(spec_text, chk)

    # Step 3: Structural checks
    structural = structural_checks(runtime, structural_rules)

    # Step 4: Determine pass/fail
    cov_ok = all(coverage[k]["coverage"] >= coverage_threshold for k in ("invariants","techniques","outputs"))
    tests_ok = (coverage["tests"]["coverage"] >= 1.0)
    struct_ok = (len(structural["issues"]) == 0)
    overall_ok = cov_ok and tests_ok and struct_ok

    # Step 5: Write report
    report = []
    report.append(f"# Prompt Sync Report\n")
    report.append(f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"- Changed inputs: {changed}\n")
    report.append(f"## Coverage\n")
    for k in ("invariants","techniques","outputs"):
        c = coverage[k]
        report.append(f"- **{k}**: {c['present']}/{c['total']} ({c['coverage']:.2%})")
        if c["missing"]:
            report.append(f"  - Missing: {', '.join(c['missing'])}")
    report.append(f"- **tests**: {coverage['tests']['present']}/{coverage['tests']['total']} ({coverage['tests']['coverage']:.2%})")
    missing_tests = [t['id'] for t in coverage['tests_detail'] if not t['passed']]
    if missing_tests:
        report.append(f"  - Failed tests: {', '.join(missing_tests)}")
    report.append("\n## Structural\n")
    report.append(f"- Length: {structural['len']} chars")
    if structural["issues"]:
        report.append(f"- Issues:")
        for i in structural["issues"]:
            report.append(f"  - {i}")
    else:
        report.append(f"- Issues: none")
    report.append(f"\n## Result: {'PASS' if overall_ok else 'FAIL'}\n")
    write_text(sync_report, "\n".join(report))

    # Step 6: Badge
    badge = {
        "coverage": {
            "invariants": coverage["invariants"]["coverage"],
            "techniques": coverage["techniques"]["coverage"],
            "outputs": coverage["outputs"]["coverage"],
            "tests": coverage["tests"]["coverage"]
        },
        "structural_ok": struct_ok,
        "status": "pass" if overall_ok else "fail"
    }
    write_text(badge_json, json.dumps(badge, indent=2))

    # Step 7: Update lockfile
    lock_update = {
        "inputs_hash": inputs_hash,
        "last_run": time.time(),
        "result": badge
    }
    write_text(lockfile, json.dumps(lock_update, indent=2))

    # Exit code for CI/pre-commit
    if "--check" in argv or "--ci" in argv:
        sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main(sys.argv[1:])
