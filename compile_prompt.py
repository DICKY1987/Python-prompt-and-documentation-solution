
import sys, os, yaml, json, re
from typing import Dict, Any, List

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def index_sections(sections, idx=None):
    if idx is None: idx = {}
    for s in sections:
        sid = s.get("id")
        if sid:
            idx[sid] = s
        if s.get("children"):
            index_sections(s["children"], idx)
    return idx

def apply_patches(spec: dict, patches: List[dict]):
    # Build ID index
    idx = index_sections(spec.get("sections", []))
    for p in patches:
        tid = p.get("target_id")
        field = p.get("field", "content")
        op = p.get("op", "replace")
        val = p.get("value", "")
        node = idx.get(tid)
        if not node:
            print(f"[WARN] Patch target_id {tid} not found; skipping.")
            continue
        cur = node.get(field, "")
        if op == "replace":
            node[field] = val
        elif op == "append":
            node[field] = (cur or "") + str(val)
        elif op == "prepend":
            node[field] = str(val) + (cur or "")
        elif op == "remove":
            node[field] = ""
        else:
            print(f"[WARN] Unknown op {op} for {tid}; skipping.")
    return spec

def render_md(sections, level=1, numbering_prefix=""):
    md = []
    for i, s in enumerate(sections, start=1):
        number = f"{numbering_prefix}{i}"
        title = s.get("title", "")
        sid = s.get("id","")
        md.append(f"# {'#'*(level-1)}{number}. {title}  [{sid}]")
        content = s.get("content", "").strip()
        if content:
            md.append(content)
            md.append("")
        if s.get("children"):
            md.append(render_md(s["children"], level+1, f"{number}."))
    return "\n".join(md)

def main():
    if len(sys.argv) < 4:
        print("Usage: python compile_prompt.py <PromptSpec.yaml> <PromptPatches.yaml|none> <out.md>")
        sys.exit(1)
    spec_path, patches_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = load_yaml(spec_path)
    patches = []
    if patches_path.lower() != "none" and os.path.exists(patches_path):
        patches = load_yaml(patches_path)
    if patches:
        spec = apply_patches(spec, patches)
    md = render_md(spec.get("sections", []))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
