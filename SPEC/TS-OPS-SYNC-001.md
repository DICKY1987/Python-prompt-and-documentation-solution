# Technical Specification — PromptOps + DocOps Sync System
**Doc ID:** TS-OPS-SYNC-001 • **Version:** 1.0.0 • **Status:** Build

## 1. Purpose & Scope  [OBJ-001]
Provide a deterministic, programmable system to keep **prompts** and **project documentation** in sync by treating them as code with structured sources, compilation, validation, and CI gates.

### In Scope
- **PromptOps**: PromptSpec → Patches → Compiler → CoverageChecker → SyncOrchestrator → CI.
- **DocOps**: DocSources (REQ/TST/ADR/GLO) → Templates/Goldens → DocBuilder → DocValidator → CI.
- **Shared**: Manifests, Schemas, Interfaces/CLI, Observability, ADRs, Governance.

### Out of Scope
Model selection/hosting; human approval workflows beyond gates.

## 2. Stakeholders & Roles  [STK-001]
- **Owner**: accepts releases, sets thresholds.
- **Engineer/Agent**: implements compilers/validators/orchestrators.
- **Docs Lead**: owns templates, goldens, glossary, style rules.
- **QA**: maintains tests, goldens, triage of failures.

## 3. Definitions  [DEF-001]
**PromptOps** — prompt as code; **DocOps** — docs as code; **Golden** — canonical example output; **ADR** — Architecture Decision Record.

## 4. Architecture Overview (ISO/IEC/IEEE 42010)  [ARC-001]
- **Development viewpoint**: YAML/JSON SSOT → compilers → Markdown outputs → gates.
- **Information viewpoint**: JSON Schemas validate PromptSpec, Checklist, SyncManifest, DocRegistry, DocManifest.
- **Decision viewpoint**: ADRs captured and cross-referenced by ID.
- **Operations viewpoint**: Orchestrators run build→check→validate, emit reports/badges/lockfiles; CI blocks on failure.

Key components:
1) PromptSpec, PromptPatches, PromptCompiler, PromptChecklist, CoverageChecker, PromptSyncOrchestrator
2) DocRegistry, DocSources (REQ/TST/ADR/GLO), Templates/Goldens, DocBuilder, DocValidator
3) ProjectSyncOrchestrator, CI Hooks (pre-commit, GitHub Actions)

## 5. Functional Requirements (ISO/IEC/IEEE 29148)  [REQ-SET]

### 5.1 PromptOps  [REQ-PROMPT]
- **REQ-PR-001 (M)**: Hierarchical, ID-addressable PromptSpec.
- **REQ-PR-002 (M)**: Patch ops: append/replace/prepend/remove/insert-before/after.
- **REQ-PR-003 (M)**: Deterministic compile → Runtime Prompt.
- **REQ-PR-004 (M)**: CoverageChecker verifies invariants/techniques/outputs/tests.
- **REQ-PR-005 (M)**: SyncOrchestrator detects input changes (hash), rebuilds, lints, emits report/badge/lockfile.
- **REQ-PR-006 (S)**: Support golden runtime prompts for format/tone stabilization.
- **REQ-PR-007 (M)**: CLI verbs: build/check/report/ci.

### 5.2 DocOps  [REQ-DOCS]
- **REQ-DC-001 (M)**: Structured DocSources: REQ, TST, ADR, GLO (+ optional IFC/PROC/FIG).
- **REQ-DC-002 (M)**: DocRegistry maps sources+templates+goldens to outputs.
- **REQ-DC-003 (M)**: DocBuilder injects tables/sections into templates.
- **REQ-DC-4 (M)**: DocValidator checks outline anchors, REQ↔TST traceability ≥ threshold, style rules.
- **REQ-DC-5 (M)**: ProjectSyncOrchestrator runs PromptOps then DocOps; any failure fails the run.
- **REQ-DC-6 (S)**: Cross-doc index (REQ↔ADR↔TST).
- **REQ-DC-7 (S)**: HTML/PDF emitters.

### 5.3 CI & Governance  [REQ-CI]
- **REQ-CI-001 (M)**: pre-commit blocks local commits on failures.
- **REQ-CI-002 (M)**: GitHub Actions blocks merges; uploads reports/badges.
- **REQ-CI-003 (S)**: PR comment with summary deltas.
- **REQ-CI-004 (S)**: Conventional Commits for changelog/semver.

## 6. Non-Functional Requirements  [NFR-SET]
Deterministic builds; machine reports/badges; performance ≤ 60s typical; no RCE; one-command UX; Python 3.11+.

## 7. Data Models & Schemas  [DATA-001]
Schemas are normative and MUST be enforced in CI:
- `schemas/prompt_spec.schema.json`  [SCH-PR-001]
- `schemas/prompt_checklist.schema.json`  [SCH-PR-002]
- `schemas/prompt_sync_manifest.schema.json`  [SCH-PR-003]
- `schemas/doc_registry.schema.json`  [SCH-DC-001]
- `schemas/doc_manifest.schema.json`  [SCH-DC-002]

## 8. Workflows  [WFL-SET]
- **PromptOps**: build → coverage → lint → report/badge/lock.
- **DocOps**: build → outline/trace/style → report/badge.
- **Unified**: project-sync runs both, fail-fast, same exit codes locally and in CI.

## 9. Interfaces (CLI & Files)  [INT-SET]
CLI verbs:
- `prompt build|check|report|ci`
- `docs build|validate|report|ci`
- `project-sync build|check|ci`

File layout (reference):
```
/prompt/{PromptSpec.yaml, PromptPatches/*.yaml, Prompt_Checklist.yaml, prompt_sync_manifest.yaml}
/docs/{sources/*.yaml, templates/*.md, goldens/*.md, registry.yaml, validators/*.yaml, out/*.md}
/SPEC/{schemas/*.json, ADR/*.md, templates/*.md, goldens/*.md}
```

## 10. CI/CD & Automation  [CICD-001]
pre-commit (local gate) and GitHub Actions (server gate) enforce the same checks; artifacts are uploaded.

## 11. Security  [SEC-001]
Parse YAML safely, sanitize template injection, no network I/O in compilers/validators, least-privileged CI tokens.

## 12. Observability  [OBS-001]
Emit human reports (Markdown) and machine badges (JSON); store input hashes in lockfiles; record build time & coverage ratios.

## 13. Goldens & Style  [GLD-001]
Each doc type includes a template + golden; style rules define banned phrases, headings, numbering, glossary usage.

## 14. Acceptance Tests  [TST-SET]
- **TST-001**: CoverageChecker meets threshold; no missing invariants.
- **TST-002**: DocValidator passes outline and traceability ≥ threshold.
- **TST-003**: Removing a required anchor fails outline validation.
- **TST-004**: Banned phrase triggers style failure.
- **TST-005**: Unified orchestrator only passes when both pipelines pass.

## 15. Versioning & Governance  [GOV-001]
SemVer for spec; ADRs for material decisions; changelog via Conventional Commits.

## 16. Initial ADRs  [ADR-SET]
- **ADR-001**: Structured Sources + Compile-Time Generation (Accepted).
- **ADR-002**: JSON Schema for Validation (Accepted).
- **ADR-003**: CI Gates via pre-commit + GitHub Actions (Accepted).

## 17. References  [REF-001]
Standards: ISO/IEC/IEEE 29148, ISO/IEC/IEEE 42010; JSON Schema 2020-12; GitHub Actions; pre-commit; Diátaxis.
