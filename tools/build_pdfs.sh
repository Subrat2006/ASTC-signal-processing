#!/usr/bin/env bash
# Build every problem-statement PDF (and the roadmap PDF) from its LaTeX source.
# Usage:  bash tools/build_pdfs.sh            # build all
#         bash tools/build_pdfs.sh 07         # build only problems whose folder starts with 07
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export TEXINPUTS="$ROOT/latex//:"
filter="${1:-}"
for dir in "$ROOT"/problems/${filter}*/; do
  [ -d "$dir" ] || continue
  tex=$(ls "$dir"/*.tex 2>/dev/null | head -n1) || true
  [ -n "${tex:-}" ] || continue
  echo ">> building $(basename "$tex")"
  ( cd "$dir" && pdflatex -interaction=nonstopmode -halt-on-error "$(basename "$tex")" >/dev/null \
      && pdflatex -interaction=nonstopmode -halt-on-error "$(basename "$tex")" >/dev/null ) \
      || { echo "!! LaTeX failed for $tex (see its .log)"; exit 1; }
  ( cd "$dir" && rm -f *.aux *.log *.out *.toc )
done
if [ -z "$filter" ] && [ -f "$ROOT/docs/Curriculum_Roadmap.tex" ]; then
  echo ">> building Curriculum_Roadmap.tex"
  ( cd "$ROOT/docs" && pdflatex -interaction=nonstopmode -halt-on-error Curriculum_Roadmap.tex >/dev/null \
     && pdflatex -interaction=nonstopmode -halt-on-error Curriculum_Roadmap.tex >/dev/null && rm -f *.aux *.log *.out *.toc )
fi
echo "done."
