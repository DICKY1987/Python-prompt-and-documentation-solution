# 1. Objective  [OBJ-001]
Create a unified IEEE 830–style SRS from overlapping docs. Maintain traceability and coverage. [INV-005][TEC-402]

# #1.1. Purpose  [OBJ-PRP-001]
Produce a single, authoritative document with strict numbering and cross-references. [INV-005]

# #1.2. Scope  [OBJ-SCP-001]
Ingestion, normalization, conflict detection/resolution, validation (internal/external), consolidation, packaging. [TEC-451] Include explicit assumptions and dependencies section.

# 2. Process (Agentic Workflow)  [PRC-001]
Plan → Execute → Verify with dual-agent loop and self-repair. [TEC-101][TEC-203][TEC-304]

# #2.1. Ingest & Normalize  [PRC-ING-001]
Parse all attachments; normalize into IEEE 830 scaffold; tag statements with {doc_id, section, line_ref}. [TEC-402]

# #2.2. Overlap & Conflict Detection  [PRC-CONF-001]
Deduplicate and detect conflicts; register conflict type and location. [TEC-402]

# #2.3. Validation Passes  [PRC-VAL-001]
Internal, External with citations, and Logical validation; prefer newest canonical sources. [TEC-451] Use multiple authoritative sources; capture URLs and publication dates.

# #2.4. Dual-Agent Loop  [PRC-DAV-001]
Generator compiles; Validator checks vs checklist and runs self-repair on failure. [TEC-203][TEC-304]

# #2.5. Quality Gates  [PRC-QG-001]
Coverage ≥95%, zero unresolved conflicts or explicitly deferred, IEEE numbering, full traceability, observability metrics. [INV-006][INV-008]

# 3. Outputs  [OUT-001]
Main SRS + Appendices + Packaging rules.

# #3.1. Main SRS  [OUT-SRS-001]
IEEE 830 Sections 1–3 with strict numbering. [INV-005]

# #3.2. Appendices  [OUT-APP-001]
A) Conflict Log; B) Traceability; C) Validation Reports; D) Coverage Metrics. [TEC-402]

# #3.3. Packaging  [OUT-PKG-001]
Emit a single Markdown SRS; export matrices as CSV and link them in an appendix index.

# 4. Guardrails  [GRD-001]
Invariants enforced in every revision.

# #4.1. Do-Not-Drop Block  [INV-001]
Ensure invariants block is present in every revision.

# #4.2. Citations for External Claims  [INV-002]
Use web research with inline citations.

# #4.3. Confirm High-Impact Actions  [INV-003]
Ask for confirmation before high-impact actions.

# #4.4. Explicit Upload Requests  [INV-004]
If inputs missing, ask the user to upload files.

# #4.5. IEEE Numbering & Glossary  [INV-005]
Enforce strict numbering and a unified glossary.

# #4.6. Conflict Resolution Policy  [INV-006]
Zero unresolved conflicts or defer explicitly with SME packet.

# #4.7. Full Traceability  [INV-007]
Final & rejected items both traceable to sources.

# #4.8. Coverage & Observability  [INV-008]
Coverage ≥95% and observability metrics logged.
