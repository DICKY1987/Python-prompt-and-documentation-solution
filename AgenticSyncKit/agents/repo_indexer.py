# agents/repo_indexer.py
from __future__ import annotations
import ast, fnmatch, json, os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import networkx as nx

class RepoIndexer:
    def __init__(self, repo_root: Path, code_globs: List[str]):
        self.root = repo_root
        self.code_globs = code_globs

    def _iter_py_files(self) -> List[Path]:
        files: List[Path] = []
        for pattern in self.code_globs:
            for p in self.root.rglob("*.py"):
                if fnmatch.fnmatch(p.as_posix(), (self.root / pattern).as_posix()):
                    files.append(p)
        return sorted(set(files))

    def _module_name(self, path: Path) -> str:
        rel = path.relative_to(self.root).as_posix().replace("/", ".")
        return rel[:-3] if rel.endswith(".py") else rel

    def _imports_in_file(self, path: Path) -> Set[str]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            return set()
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports

    def build_graph(self):
        G = nx.DiGraph()
        files = self._iter_py_files()
        mod_by_file = {f: self._module_name(f) for f in files}
        for f, m in mod_by_file.items():
            G.add_node(m, file=f.as_posix())
        for f, m in mod_by_file.items():
            imps = self._imports_in_file(f)
            for other_m in imps:
                if other_m in G:
                    G.add_edge(other_m, m)
        return G

    def topo_order(self, G):
        return list(nx.topological_sort(G))

    def changed_files(self) -> Set[str]:
        try:
            import subprocess
            res = subprocess.run(["git","diff","--name-only","HEAD~1"], cwd=self.root, capture_output=True, text=True, check=False)
            return set([l.strip() for l in res.stdout.splitlines() if l.strip() and l.strip().endswith(".py")])
        except Exception:
            return set()

    def impacted_modules(self, G) -> Set[str]:
        changed = self.changed_files()
        if not changed:
            return set()
        file_to_mod = {G.nodes[n]["file"]: n for n in G.nodes}
        changed_mods = set()
        for cf in changed:
            p = (self.root / cf).as_posix()
            m = file_to_mod.get(p)
            if m:
                changed_mods.add(m)
        impacted = set(changed_mods)
        for m in list(G.nodes):
            for src in changed_mods:
                if nx.has_path(G, src, m):
                    impacted.add(m)
        return impacted

    def write_artifacts(self, G, out_dir: Path):
        out_dir.mkdir(parents=True, exist_ok=True)
        topo = self.topo_order(G)
        impacted = sorted(self.impacted_modules(G))
        graph = {
            "nodes":[{"id": n, "file": G.nodes[n]["file"]} for n in G.nodes],
            "edges":[{"src": u, "dst": v} for u,v in G.edges],
            "topological_order": topo,
            "impacted": impacted,
        }
        (out_dir / "repo_graph.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")
        return graph
