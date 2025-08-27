#!/usr/bin/env python3
import json, sys, os, textwrap

def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def pct(x):
    try:
        return f"{float(x)*100:.0f}%"
    except Exception:
        return "—"

prompt_badge = load_json("badges_prompt_status.json")
doc_badge = load_json("docs/out/doc_badge.json")

prompt_status = prompt_badge.get("status","unknown")
doc_status = doc_badge.get("status","unknown")

p_cov = prompt_badge.get("coverage", {})
d_docs = doc_badge.get("docs", [])

sync_report = load("sync_report.md")
doc_report = load("docs/out/doc_sync_report.md")

lines = []
lines.append("## ✅ Project Sync Status")
lines.append("")
lines.append(f"**PromptOps:** `{prompt_status}`  |  **DocOps:** `{doc_status}`")
lines.append("")
if p_cov:
    lines.append("**Prompt coverage:**")
    lines.append(f"- Invariants: {pct(p_cov.get('invariants'))}")
    lines.append(f"- Techniques: {pct(p_cov.get('techniques'))}")
    lines.append(f"- Outputs: {pct(p_cov.get('outputs'))}")
    lines.append(f"- Tests pass ratio: {pct(p_cov.get('tests'))}")
    lines.append("")
if d_docs:
    lines.append("**Docs:**")
    for d in d_docs:
        ok = d.get("outline_ok") and d.get("trace_ok") and not d.get("issues")
        lines.append(f"- `{d.get('id')}` → {'PASS' if ok else 'FAIL'} | Traceability: {pct(d.get('trace_coverage'))}")
    lines.append("")

lines.append("<details><summary>Prompt Sync Report</summary>")
lines.append("")
lines.append(sync_report or "_(no report found)_")
lines.append("")
lines.append("</details>")
lines.append("")
lines.append("<details><summary>Doc Sync Report</summary>")
lines.append("")
lines.append(doc_report or "_(no report found)_")
lines.append("")
lines.append("</details>")

out = "\n".join(lines)
with open("PR_COMMENT.md", "w", encoding="utf-8") as f:
    f.write(out)
print("Wrote PR_COMMENT.md")
