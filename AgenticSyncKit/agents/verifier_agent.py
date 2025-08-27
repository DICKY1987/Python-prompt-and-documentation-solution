# agents/verifier_agent.py
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Tuple

class Verifier:
    def __init__(self, repo_root: Path):
        self.root = repo_root

    def run_docops(self) -> Tuple[bool, str]:
        r = subprocess.run(["python","docs/builders/build_docs.py"], cwd=self.root, capture_output=True, text=True)
        ok_build = (r.returncode == 0)
        out = r.stdout + "\n" + r.stderr
        g = subprocess.run(["python","tools/golden_diff.py"], cwd=self.root, capture_output=True, text=True)
        ok_golden = (g.returncode == 0)
        out += "\n[GOLDEN]\n" + g.stdout + g.stderr
        t = subprocess.run(["python","tools/cross_domain_technique_check.py"], cwd=self.root, capture_output=True, text=True)
        ok_tecs = (t.returncode == 0)
        out += "\n[TECHNIQUES]\n" + t.stdout + t.stderr
        i = subprocess.run(["python","tools/id_integrity_check.py"], cwd=self.root, capture_output=True, text=True)
        ok_ids = (i.returncode == 0)
        out += "\n[IDS]\n" + i.stdout + i.stderr
        f = subprocess.run(["python","tools/fingerprint_sync.py"], cwd=self.root, capture_output=True, text=True)
        ok_fp = (f.returncode == 0)
        out += "\n[FINGERPRINT]\n" + f.stdout + f.stderr
        ok = ok_build and ok_golden and ok_tecs and ok_ids and ok_fp
        return ok, out

    def run_promptops(self) -> Tuple[bool, str]:
        py = self.root / "project_sync_orchestrator.py"
        if py.exists():
            r = subprocess.run(["python","project_sync_orchestrator.py"], cwd=self.root, capture_output=True, text=True)
            return (r.returncode == 0), r.stdout + r.stderr
        return True, "[SKIP] project_sync_orchestrator.py missing"

    def verify_all(self) -> Tuple[bool, str]:
        ok_docs, out_docs = self.run_docops()
        ok_prompt, out_prompt = self.run_promptops()
        ok = ok_docs and ok_prompt
        return ok, out_docs + "\n" + out_prompt
