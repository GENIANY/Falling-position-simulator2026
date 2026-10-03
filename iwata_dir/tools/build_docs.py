#!/usr/bin/env python3
"""Build the current planning Markdown -> TeX -> PDF.
Requires pandoc, XeLaTeX, TeX packages, and fonts described in docs/BUILD.md.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    for tool in ("pandoc", "xelatex"):
        if shutil.which(tool) is None:
            parser.error(f"Required command not found: {tool}. See docs/BUILD.md.")
    source = root / "docs/PROJECT_PLAN.md"
    template = root / "tools/template.tex"
    if not source.is_file() or not template.is_file():
        parser.error("Missing Markdown source or TeX template.")
    tex = root / "docs/PROJECT_PLAN.tex"
    try:
        subprocess.run([
            "pandoc", str(source), "--standalone", "--from=markdown", "--to=latex",
            "--template=" + str(template), "--no-highlight", "--eol=lf", "-o", str(tex)
        ], check=True, timeout=120)
        with tempfile.TemporaryDirectory(prefix="balloon-doc-build-") as temporary:
            for _ in range(3):
                run = subprocess.run([
                    "xelatex", "-no-shell-escape", "-interaction=nonstopmode",
                    "-halt-on-error", "-output-directory=" + temporary, str(tex)
                ], cwd=root, check=False, capture_output=True, text=True, timeout=120)
                if run.returncode:
                    print(run.stdout[-9000:], file=sys.stderr)
                    print(run.stderr[-3000:], file=sys.stderr)
                    return run.returncode
            built = Path(temporary) / "PROJECT_PLAN.pdf"
            if not built.is_file() or built.stat().st_size == 0:
                raise RuntimeError("No non-empty PDF was produced.")
            shutil.copy2(built, root / "docs" / built.name)
            log = (Path(temporary) / "PROJECT_PLAN.log").read_text(errors="replace")
            warnings = [line for line in log.splitlines() if "Overfull" in line or "Missing character" in line]
            for line in warnings:
                print("REVIEW:", line)
        print("Built current docs/PROJECT_PLAN.tex and PDF. No repository commit was made.")
        print("Inspect the rendered PDF before publishing a new snapshot.")
        return 0
    except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
