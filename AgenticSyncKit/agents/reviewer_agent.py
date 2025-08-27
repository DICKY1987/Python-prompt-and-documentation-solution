# agents/reviewer_agent.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from .llm_client import call_llm

SYSTEM = """You are a precise documentation reviewer. Output MUST be a unified diff patch ONLY.
Target source files (YAML/MD under docs/sources or templates), not compiled outputs.
Follow style rules: no "we will try", "maybe", "sort of". Keep changes minimal and deterministic.
"""

PROMPT_TMPL = """Repository root: {repo}
Impacted topics: {impacted}

Constraints:
- Only patch structured sources (YAML under docs/sources, templates under docs/templates). 
- Keep anchors and IDs stable.
- If something is missing, add it to the correct structured file (e.g., techniques.yaml, requirements.yaml).

Provide a minimal set of patches as a unified diff.
"""

def propose_patches(repo_root: Path, impacted: list[str]) -> str:
    prompt = PROMPT_TMPL.format(repo=repo_root.as_posix(), impacted=", ".join(impacted) or "(full)")
    return call_llm(SYSTEM, prompt)

def save_patch(patch_text: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(patch_text, encoding="utf-8")
    return out_path
