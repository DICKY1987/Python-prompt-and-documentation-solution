
# Prompt Engineering Programmatic Toolkit (Starter)

This starter lets you **standardize**, **programmatically modify**, and **evaluate** prompts using **Python + YAML**.

## What’s inside
- `PromptSpec.yaml` — structured prompt spec with hierarchical IDs.
- `PromptPatches_example.yaml` — example patch operations (`append`, `replace`, `prepend`, `remove`) by `target_id`.
- `compile_prompt.py` — builds a runtime Markdown prompt with numbered sections from the spec (+ optional patches).
- `model_adapter.py` — stub where you plug your LLM.
- `eval_harness.py` — structural + behavioral test harness.
- `prompt_schema_min.json` — minimal JSON Schema (optional) for sanity checks.

## Workflow
1. **Edit** `PromptSpec.yaml` (or add small, reviewable changes via `PromptPatches_example.yaml`).
2. **Compile**
   ```bash
   python compile_prompt.py PromptSpec.yaml PromptPatches_example.yaml Runtime_Prompt.md
   ```
3. **Validate structure & coverage** (use your existing coverage checker):
   ```bash
   python prompt_coverage_checker.py Prompt_Spec_v1.0.md Prompt_Checklist_v1.0.yaml prompt_coverage_report.csv
   ```
4. **Evaluate**
   - Structural checks:
     ```bash
     python eval_harness.py
     ```
   - Behavioral tests: add `tests/inputs/*.md` then integrate your LLM in `model_adapter.py`.

## Tips
- Keep edits atomic via patch files—this preserves auditability and prevents regressions.
- Use stable IDs forever. Update text, not identifiers.
- Gate merges with coverage + structural checks in CI (pre-commit, GitHub Actions).
