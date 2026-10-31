"""Print cyclomatic complexity (McCabe) for functions in given Python files.

Stdlib only. Target CC ≤ 10; too high > 15 (exit 2).

Usage (repo root):
    python scripts/score_cc.py src/foo.py
    python scripts/score_cc.py --fail-above 15 src/foo.py
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_CC = 10
TOO_HIGH_CC = 15


def function_complexity(node: ast.AST) -> int:
    """McCabe-style cyclomatic complexity."""

    class _Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.cc = 1

        def visit_If(self, n: ast.If) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_For(self, n: ast.For) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_AsyncFor(self, n: ast.AsyncFor) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_While(self, n: ast.While) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_ExceptHandler(self, n: ast.ExceptHandler) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_Assert(self, n: ast.Assert) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_IfExp(self, n: ast.IfExp) -> None:
            self.cc += 1
            self.generic_visit(n)

        def visit_BoolOp(self, n: ast.BoolOp) -> None:
            self.cc += max(0, len(n.values) - 1)
            self.generic_visit(n)

        def visit_comprehension(self, n: ast.comprehension) -> None:
            self.cc += 1
            self.cc += len(n.ifs)
            self.generic_visit(n)

        def visit_Match(self, n: ast.Match) -> None:
            self.cc += max(0, len(n.cases) - 1)
            self.generic_visit(n)

    visitor = _Visitor()
    visitor.visit(node)
    return visitor.cc


def parse_functions(rel_path: str, source: str) -> list[tuple[str, int, int]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    module = rel_path[:-3].replace("/", ".") if rel_path.endswith(".py") else rel_path
    out: list[tuple[str, int, int]] = []

    def add(fn: ast.FunctionDef | ast.AsyncFunctionDef, class_name: str | None) -> None:
        if fn.name.startswith("__") and fn.name.endswith("__"):
            return
        qual = f"{module}:{class_name}.{fn.name}" if class_name else f"{module}:{fn.name}"
        out.append((qual, int(fn.lineno), function_complexity(fn)))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(node, None)
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add(child, node.name)
    return out


def _py_files(raw_paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for raw in raw_paths:
        path = raw if raw.is_absolute() else ROOT / raw
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        elif path.suffix == ".py":
            files.append(path)
    return files


def _flag(cc: int, fail_above: int) -> str:
    if cc > fail_above:
        return " TOO_HIGH"
    if cc > TARGET_CC:
        return " above_target"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Score McCabe CC on Python functions")
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories")
    parser.add_argument(
        "--fail-above",
        type=int,
        default=TOO_HIGH_CC,
        help=f"Exit 2 if any function CC is above this (default {TOO_HIGH_CC})",
    )
    args = parser.parse_args()
    rows: list[tuple[int, str, int, str]] = []
    worst = 0
    for path in _py_files(args.paths):
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"FAIL: {path}: {exc}")
            return 1
        for qual, lineno, cc in parse_functions(rel, source):
            worst = max(worst, cc)
            rows.append((cc, qual, lineno, _flag(cc, args.fail_above)))
    rows.sort(key=lambda r: (-r[0], r[1]))
    for cc, name, line, flag in rows:
        print(f"CC={cc:3d}  L{line:<5} {name}{flag}")
    print(f"functions={len(rows)} worst={worst} target<={TARGET_CC} too_high>{args.fail_above}")
    if any(r[3] == " TOO_HIGH" for r in rows):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
