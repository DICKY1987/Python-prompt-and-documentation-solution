# 1. Introduction  [SEC-INTRO]
Provide context and goals.

# 2. Overall Description  [SEC-OVERVIEW]
High-level system overview and scope.

# 3. Specific Requirements  [SEC-REQS]
| ID | Title | Text |
|---|---|---|
| REQ-001 | Unified Source-of-Truth for Docs | All project documentation must be authored in structured YAML with stable IDs and compiled into Markdown/PDF as build artifacts. |
| REQ-002 | Traceability Matrix | Each requirement must link to at least one test case and any related decision records. |
| REQ-003 | Standardized Output Using Goldens | Each document type must have a golden exemplar; builds must match the golden’s outline and section labels. |

# 4. Glossary  [SEC-GLOSSARY]
| Term | Definition |
|---|---|
| SSOT | Single Source of Truth for documentation and prompts. |
| Golden | A canonical example output used for standardization. |

# 5. Traceability Matrix  [SEC-TRACE]
| REQ ID | Covered By Tests |
|---|---|
| REQ-001 | - |
| REQ-002 | TST-001 |
| REQ-003 | - |