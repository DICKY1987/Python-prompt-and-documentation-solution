#!/usr/bin/env python3
import subprocess, sys, time
from pathlib import Path

BASE = Path(".")

ARTIFACTS = {
    "Runtime_Prompt.md": [
        "PromptSpec.yaml",
        "PromptPatches",
        "Prompt_Checklist.yaml",
        "Prompt_Checklist_v1.0.yaml",
        "prompt/prompt_sync_manifest.yaml",
        "sync_manifest.yaml",
    ],
    "docs/out/SRS.md": [
        "docs/sources",
        "docs/templates/SRS_template.md",
        "docs/goldens/SRS_golden.md",
        "docs/registry.yaml",
        "doc_manifest.yaml",
    ]
}

def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except FileNotFoundError:
        return 0.0

def newest_under(path: Path) -> float:
    if path.is_file():
        return mtime(path)
    latest = 0.0
    if path.exists():
        for pp in path.rglob("*"):
            if pp.is_file():
                latest = max(latest, mtime(pp))
    return latest

def check_mtime():
    errors = []
    for out, inputs in ARTIFACTS.items():
        outp = BASE / out
        if not outp.exists():
            if any((BASE / i).exists() for i in inputs):
                errors.append(f"{out} missing but inputs exist; run build")
            continue
        latest_in = 0.0
        for i in inputs:
            ip = BASE / i
            latest_in = max(latest_in, newest_under(ip))
        if latest_in and mtime(outp) < latest_in:
            errors.append(f"{out} is older than its inputs; rebuild required")
    return errors

def changed_files():
    cmd = ["git", "diff", "--name-only", "--staged"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    if not lines:
        res = subprocess.run(["git","diff","--name-only","HEAD~1"], capture_output=True, text=True)
        lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    return set(lines)

def map_impacts(changes):
    impacted = set()
    for out, inputs in ARTIFACTS.items():
        for i in inputs:
            for c in changes:
                if c.startswith(i):
                    impacted.add(out)
    return impacted

def outputs_changed(changes):
    outs = { "Runtime_Prompt.md", "docs/out/SRS.md" }
    return outs.intersection(changes)

def main():
    errs = []
    errs += check_mtime()
    changes = changed_files()
    if changes:
        impacted = map_impacts(changes)
        out_changes = outputs_changed(changes)
        for art in impacted:
            if art not in out_changes:
                errs.append(f"Impact analysis: inputs changed but artifact not updated in commit: {art}")
    if errs:
        print("Impact analysis found issues:")
        for e in errs: print("-", e)
        sys.exit(1)
    print("Impact analysis passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
