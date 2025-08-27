# agents/patch_applier.py
from __future__ import annotations
import subprocess
from pathlib import Path

def apply_unified_diff(patch_path: Path, repo_root: Path) -> bool:
    if not patch_path.exists():
        return False
    try:
        res = subprocess.run(["git","apply", "--index", patch_path.as_posix()], cwd=repo_root, capture_output=True, text=True)
        if res.returncode == 0:
            return True
        res2 = subprocess.run(["patch","-p0","-i", patch_path.as_posix()], cwd=repo_root, capture_output=True, text=True)
        return res2.returncode == 0
    except Exception:
        return False
