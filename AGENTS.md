# AGENTS.md — Operating Rules for Repo‑Aware AI Agents

This repository implements a prompt + documentation synchronization system.
These rules let an AI coding agent (e.g., ChatGPT “Codex” repo tasks or a CLI agent)
work autonomously while staying safe, deterministic, and auditable.

## Repo Map (key files the agent should learn)
- Prompts/specs: `PromptSpec.yaml`, `Prompt_Spec_v1.0 (1).md`, `Prompt_Checklist_v1.0 (1).yaml`, `PromptPatches_example.yaml`
- Orchestration: `sync_orchestrator.py`, `project_sync_orchestrator.py`, `compile_prompt.py`, `model_adapter.py`
- Validation & eval: `eval_harness.py`, `prompt_coverage_checker.py`, `prompt_schema_min.json`, `tests.yaml`, `prompt_coverage_report.csv`
- Documentation control: `doc_manifest.yaml`, `sync_manifest.yaml`, `doc_badge.json`, `badges_prompt_status.json`, `glossary.yaml`, `ontology.yaml`, `style_rules.yaml`
- SRS materials: `SRS_template.md`, `SRS_golden.md`, `SRS.md`
- CI examples: `.github/workflows/ci.yml`
- Build/utility: `Makefile`

> If a file isn’t present yet, the agent may create it while keeping changes small and testable.

## Environment Setup
1. Python 3.11+
2. Install dependencies (best‑effort):
   - If `requirements.txt` exists: `pip install -r requirements.txt`
   - Always ensure: `pip install pyyaml jsonschema`
3. Optional but recommended: `ruff` for formatting/lint (`pip install ruff`)

## Standard Commands (the agent should run these)
- **Validate prompts**: `python tools/validate_prompts.py --schema prompt_schema_min.json`
- **Run evals**: `python eval_harness.py` (if present)
- **Sync docs**: `python sync_orchestrator.py --manifest doc_manifest.yaml` (if present)
- **Build SRS**: `python project_sync_orchestrator.py --template SRS_template.md --out SRS.md` (if present)

## PR Acceptance Checks (must pass before proposing a PR)
- ✅ No syntax errors; if `ruff` is available, formatting/lint is clean.
- ✅ All prompt YAMLs conform to `prompt_schema_min.json` via `tools/validate_prompts.py`.
- ✅ Evals pass or show a net‑positive diff vs baseline (when `eval_harness.py` exists).
- ✅ `sync_orchestrator.py` runs cleanly with the manifest (no uncommitted changes afterward).
- ✅ `project_sync_orchestrator.py` successfully regenerates `SRS.md`; diffs to `SRS_golden.md` are either justified or rejected with a clear rationale in the PR description.
- ✅ Any change that affects docs also updates `README_Starter.md` and any listed files in `doc_manifest.yaml`.

## Change Policy
- Keep PRs small (≤ 300 changed LOC); group changes by concern.
- Include tests/evals when feasible; for new features, update `tests.yaml`.
- Maintain traceability: reference the spec/prompt lines that justify code/doc edits.

## Safety & Boundaries
- Default to **no network access** unless a task explicitly requires it.
- Never exfiltrate repo contents.
- For risky refactors, open a draft PR with a step‑plan before code changes.

## Agent Hints
- Prefer deterministic generation: same inputs ⇒ same outputs.
- Use `glossary.yaml` and `ontology.yaml` to keep naming consistent.
- Follow `style_rules.yaml` for documents; reject changes that violate style unless the PR includes a justified style update.
