#!/usr/bin/env python3
import subprocess, sys, os

ARTIFACT_PATHS = ["docs/out", "Runtime_Prompt.md", "sync_report.md", "docs/out/doc_sync_report.md"]

def changed_artifacts():
    try:
        # List tracked changes in artifact paths
        cmd = ["git", "diff", "--name-only", "--"] + ARTIFACT_PATHS
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        changed = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        return changed
    except Exception as e:
        print(f"[WARN] git diff not available: {e}")
        return []

def main():
    changed = changed_artifacts()
    if changed:
        print("Manual edits detected in build artifacts:")
        for c in changed:
            print(f"- {c}")
        print("Re-run the build to regenerate artifacts and commit those changes, or stop tracking artifacts.")
        sys.exit(1)
    print("No manual edits detected in build artifacts.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
