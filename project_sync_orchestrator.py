
#!/usr/bin/env python3
import os, sys, subprocess, json
from pathlib import Path

def run(cmd, cwd="."):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def main(args):
    base = Path(".")
    # Build docs
    rc, out, err = run([sys.executable, "docs/builders/build_docs.py"], cwd=base.as_posix())
    print(out.strip())
    if rc != 0:
        print(err)
        sys.exit(rc)
    # Run prompt sync if present
    if (base / "sync_orchestrator.py").exists():
        rc2, out2, err2 = run([sys.executable, "sync_orchestrator.py", "--check"], cwd=base.as_posix())
        print(out2.strip())
        if rc2 != 0:
            print(err2)
            sys.exit(rc2)
    # Validate docs
    rc3, out3, err3 = run([sys.executable, "docs/validators/validate_docs.py"], cwd=base.as_posix())
    print(out3.strip())
    if rc3 != 0:
        print(err3)
        sys.exit(rc3)
    print("Project sync complete.")
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
