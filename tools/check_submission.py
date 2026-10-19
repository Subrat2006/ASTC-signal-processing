#!/usr/bin/env python3
"""Check that a solution folder is complete.

Usage: python tools/check_submission.py 07
"""
import sys
import json
from pathlib import Path

from problem_meta import ROOT, load_problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    nn = argv[1].zfill(2)
    prob = next((p for p in load_problems() if p["nn"] == nn), None)
    if prob is None:
        print(f"No problem {nn}")
        return 2
    d = ROOT / "solutions" / prob["folder"]
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  [ok]   " if cond else "  [MISS] ") + msg)
        ok &= bool(cond)

    print(f"Checking solutions/{prob['folder']}")
    nbs = sorted(d.glob("*.ipynb"))
    check(nbs, "at least one notebook (*.ipynb)")
    for nb in nbs:
        try:
            data = json.loads(nb.read_text(encoding="utf-8"))
            cells = data.get("cells", [])
            code = [c for c in cells if c.get("cell_type") == "code"]
            executed = [c for c in code if c.get("execution_count")]
            src = "\n".join("".join(c.get("source", "")) for c in code)
            check(code and len(executed) == len(code), f"{nb.name}: all code cells executed (run all)")
            check("seed" in src.lower() or "get_rng" in src, f"{nb.name}: random seed is set")
            check(nb.stat().st_size < 5_000_000, f"{nb.name}: smaller than 5 MB")
        except Exception as exc:  # noqa: BLE001
            check(False, f"{nb.name}: could not be parsed ({exc})")
    check(any(d.glob("report.*")), "report.md or report.pdf")
    check((d / "memo.md").exists() or any(d.glob("memo.*")), "memo (deliverable D6)")
    check((d / "figures").is_dir() and any((d / "figures").iterdir()), "figures/ with at least one figure")
    readme = (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").exists() else ""
    check("Sources and AI-tool usage" in readme and "_List every paper" not in readme,
          "README: sources and AI-tool usage filled in")
    unchecked = readme.count("- [ ]")
    print(f"  {unchecked} unchecked items remain in the README checklist")
    print("RESULT:", "complete" if ok else "incomplete")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
