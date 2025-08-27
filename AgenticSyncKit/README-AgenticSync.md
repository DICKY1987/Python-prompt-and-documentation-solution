# AgenticSyncKit — Zero-touch Integration Plan

This kit adds three patterns into your repo:
1) **RepoAgent-style** code indexer with topological order + impact plan.
2) **DocAider-style** Reviewer→Revise stage that proposes **unified diff patches** against structured sources.
3) **DocAgent-style** Verifier loop that runs your hard gates (golden diff, ID integrity, fingerprint, techniques) to guarantee **Absolute Sync**.

## One-time drop-in (Codex steps)

1. Copy the kit into the repo root (or unzip at `/` of the repo):
   - `agents/`, `config/agentic_config.yaml`, `run_agentic_pipeline.py`, `requirements-agentic.txt`
   - `workflows/agentic_sync.yml` → place under `.github/workflows/agentic_sync.yml`
   - `scripts/bootstrap_agentic.sh`

2. Install and run locally (sandbox, no network needed):
   ```bash
   bash scripts/bootstrap_agentic.sh
   python run_agentic_pipeline.py
   ```

   - Indexer writes `agents/out/repo_graph.json` (module DAG + impacted nodes).
   - Reviewer creates `agents/out/reviewer.patch` (MOCK by default) and auto-applies if it’s a valid diff.
   - Verifier rebuilds docs, runs golden/IDs/fingerprint/techniques checks, and fails if anything drifts.

3. Enable CI (GitHub Actions):
   - Move `workflows/agentic_sync.yml` to `.github/workflows/agentic_sync.yml`.
   - Push a branch; CI will run with `LLM_PROVIDER=MOCK` (deterministic).

4. (Optional) Enable real LLM:
   - Set `LLM_PROVIDER=OPENAI` (or your provider) and implement the adapter in `agents/llm_client.py`.
   - Keep temperature at `0.0` to preserve determinism.

## Modes
- **Sandbox** (default): `mode: sandbox` in `config/agentic_config.yaml` (no git push).
- **Repo**: set `mode: repo` and provide git settings; the pipeline will branch, commit, and push.

## Safety & Determinism
- Reviewer is constrained to edit only **structured sources** (YAML/MD under `docs/sources` or `docs/templates`).
- Verifier enforces **strict golden diff**, **ID integrity**, **sync fingerprint**, **technique cross-links**.
- This preserves your "Absolute Sync" contract: no hand-edits to artifacts, no silent ID drops, all cross-domain links intact.

## Files
- `agents/repo_indexer.py` — builds DAG + impacted plan.
- `agents/reviewer_agent.py` — proposes patches (unified diff).
- `agents/patch_applier.py` — applies patches via `git apply` (or `patch` fallback).
- `agents/verifier_agent.py` — runs deterministic validation loop.
- `agents/llm_client.py` — pluggable client (MOCK by default).
- `config/agentic_config.yaml` — knobs for mode, globs, reviewer, git.
- `workflows/agentic_sync.yml` — CI integration job.
- `requirements-agentic.txt` — extra libs (networkx, GitPython, etc.).

## Hand-off Note for Codex
Follow the steps above exactly. If CI fails, inspect artifacts:
- `agents/out/reviewer.patch` (what the Reviewer proposed)
- `agents/out/verifier.log` (why Verifier failed)
- `agents/out/repo_graph.json` (what was impacted)
