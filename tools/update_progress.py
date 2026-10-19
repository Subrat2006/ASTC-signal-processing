#!/usr/bin/env python3
"""Refresh the Status column of PROGRESS.md while preserving your scores and comments."""
import re

from problem_meta import ROOT, load_problems
from generate_docs import detect_status, pdf_link


def main():
    path = ROOT / "PROGRESS.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    kept = {}
    for line in old.splitlines():
        m = re.match(r"\| (\d\d) \|", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 7:
                kept[m.group(1)] = cells[4:7]
    out = [
        "# Progress tracker\n",
        "Status is detected automatically by `python tools/update_progress.py` (notebook present = *In progress*; "
        "notebook **and** `report.md`/`report.pdf` present = *Submitted*). Fill in the scores and comment by hand; "
        "they are preserved when this file is refreshed.\n",
        "| # | Problem | Level | Status | Self-score /100 | Mentor score /100 | Comment |",
        "|---|---|---|---|---|---|---|",
    ]
    done = 0
    for p in load_problems():
        s, m, c = kept.get(p["nn"], ["", "", ""])
        status = detect_status(p)
        done += status == "Submitted"
        out.append(f"| {p['nn']} | [{p['title']}]({pdf_link(p)}) | {p['level']} | {status} | {s} | {m} | {c} |")
    total = len(load_problems())
    out.append(f"\n**{done} of {total} problems submitted.**\n")
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"PROGRESS.md updated: {done}/{total} submitted")


if __name__ == "__main__":
    main()
