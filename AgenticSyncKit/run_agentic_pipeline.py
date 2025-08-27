# run_agentic_pipeline.py
from __future__ import annotations
import os, sys, yaml, subprocess
from pathlib import Path

from agents.repo_indexer import RepoIndexer
from agents.reviewer_agent import propose_patches, save_patch
from agents.patch_applier import apply_unified_diff
from agents.verifier_agent import Verifier

def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)

def main():
    repo = Path(".").resolve()
    cfg = yaml.safe_load((repo / "config" / "agentic_config.yaml").read_text(encoding="utf-8"))

    mode = cfg.get("mode","sandbox")
    code_globs = cfg.get("code_globs", ["**/*.py"])
    reviewer_cfg = cfg.get("reviewer", {"enable": True, "output_patch":"agents/out/reviewer.patch"})
    verifier_cfg = cfg.get("verifier", {"enable": True})

    indexer = RepoIndexer(repo, code_globs)
    G = indexer.build_graph()
    graph = indexer.write_artifacts(G, repo / "agents" / "out")
    impacted = graph.get("impacted", [])

    patch_path = repo / reviewer_cfg.get("output_patch", "agents/out/reviewer.patch")
    if reviewer_cfg.get("enable", True):
        patch_text = propose_patches(repo, impacted)
        save_patch(patch_text, patch_path)
        text = patch_text.strip()
        if text and ("--- " in text and "+++" in text):
            ok = apply_unified_diff(patch_path, repo)
            print(f"[apply patch] {'OK' if ok else 'FAILED'}")
        else:
            print("[apply patch] SKIP (no diff detected)")

    sh(["python","docs/builders/build_docs.py"], repo)

    if verifier_cfg.get("enable", True):
        v = Verifier(repo)
        ok, out = v.verify_all()
        (repo / "agents" / "out" / "verifier.log").write_text(out, encoding="utf-8")
        print(out)
        if not ok:
            print("[verifier] FAILED")
            sys.exit(1)

    if mode == "repo":
        branch = cfg.get("git", {}).get("branch", "feature/agentic-sync")
        commit_msg = cfg.get("git", {}).get("commit_message", "feat(agents): agentic sync update")
        push = cfg.get("git", {}).get("push", True)
        subprocess.run(["git","checkout","-B", branch], cwd=repo)
        subprocess.run(["git","add","-A"], cwd=repo)
        subprocess.run(["git","commit","-m", commit_msg], cwd=repo)
        if push:
            subprocess.run(["git","push","-u","origin", branch], cwd=repo)
    print("[agentic pipeline] DONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
