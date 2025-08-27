
"""
eval_harness.py
Offline: structural checks (length, banned terms, coverage hooks).
Online: plug-in your model via model_adapter.send_prompt.
"""
import os, re, yaml, json
from typing import List, Dict
from model_adapter import send_prompt

def run_structural_checks(prompt_path: str) -> Dict:
    text = open(prompt_path, "r", encoding="utf-8").read()
    issues = []
    # Example rules
    if len(text) > 15000:
        issues.append("Prompt too long (>15k chars).")
    banned = ["we will try", "maybe", "sort of"]
    for b in banned:
        if b in text.lower():
            issues.append(f"Banned phrase found: {b}")
    return {"len": len(text), "issues": issues}

def run_behavioral_tests(prompt_path: str, inputs_dir: str) -> List[Dict]:
    text = open(prompt_path, "r", encoding="utf-8").read()
    results = []
    for fname in sorted(os.listdir(inputs_dir)):
        if not fname.endswith(".md"): continue
        case_text = open(os.path.join(inputs_dir, fname), "r", encoding="utf-8").read()
        output = send_prompt(text + "\n\n" + case_text)
        # Example heuristic: output must mention "IEEE" if the input asks for SRS
        score = 1.0 if ("srs" in case_text.lower() and "ieee" in output.lower()) else 0.5
        results.append({"case": fname, "score": score, "passed": score >= 0.7})
    return results

if __name__ == "__main__":
    prompt_path = "Runtime_Prompt.md"
    print(run_structural_checks(prompt_path))
    # To run behavioral tests, create tests/inputs/*.md and then:
    # print(run_behavioral_tests(prompt_path, "tests/inputs"))
