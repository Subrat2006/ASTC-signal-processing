"""Parse the machine-readable metadata (%% META key=value lines) and the deliverable
list out of every problem-statement .tex file. Single source of truth for the docs."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    "A": "Foundations: Signals, Sensors and Sampling",
    "B": "Mathematics of Signals and Systems",
    "C": "Electronics for Signal Processing",
    "D": "Digital Signal Processing",
    "E": "Machine Learning for Signals and Capstone",
}
LEVELS = {1: "Foundations", 2: "Core", 3: "Advanced", 4: "Expert", 5: "Capstone"}
CAPSTONE_ID = 25


def _tex_to_text(s: str) -> str:
    s = s.replace("--", "–")
    s = s.replace("\\_", "_").replace("\\&", "&").replace("\\'", "'")
    s = re.sub(r"\\['\"]([A-Za-z])", r"\1", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s)
    return s.strip()


def prereq_numbers(prereq: str, pid: int):
    """Extract problem numbers from a prerequisite string ('Problems 01--03', '05, 12')."""
    if pid == CAPSTONE_ID:
        return list(range(1, CAPSTONE_ID))
    nums = set()
    for a, b in re.findall(r"(\d{2})--(\d{2})", prereq):
        nums.update(range(int(a), int(b) + 1))
    cleaned = re.sub(r"\d{2}--\d{2}", "", prereq)
    nums.update(int(x) for x in re.findall(r"\b(\d{2})\b", cleaned))
    return sorted(n for n in nums if n < pid)


def load_problems():
    problems = []
    for tex in sorted((ROOT / "problems").glob("*/*.tex")):
        text = tex.read_text(encoding="utf-8")
        meta = dict(re.findall(r"^%% META (\w+)=(.*)$", text, flags=re.M))
        pid = int(meta["id"])
        delivs = re.findall(r"\\item\[(D\d+|Bonus)\]\s*\\textbf\{([^}]*)\}", text)
        lo, hi = [float(x) for x in re.findall(r"[\d.]+", meta["effort"])[:2]]
        tasks_block = re.search(r"\\begin\{tasks\}(.*?)\\end\{tasks\}", text, flags=re.S).group(1)
        task_titles = re.findall(r"\\item\s*\\textbf\{([^}]*)\}", tasks_block)
        problems.append(
            dict(
                id=pid,
                nn=f"{pid:02d}",
                slug=meta["slug"],
                title=_tex_to_text(meta["title"]),
                part=meta["part"],
                level=int(meta["level"]),
                effort=_tex_to_text(meta["effort"]),
                hours=(lo + hi) / 2,
                prereq_text=_tex_to_text(meta["prereq"]),
                prereqs=prereq_numbers(meta["prereq"], pid),
                theory=_tex_to_text(meta["theory"]),
                skills=_tex_to_text(meta["skills"]),
                deliverables=[(k, _tex_to_text(t).rstrip(":")) for k, t in delivs],
                n_tasks=len(task_titles),
                task_titles=[_tex_to_text(t).rstrip(".") for t in task_titles],
                tex=str(tex.relative_to(ROOT)),
                pdf=str(tex.with_suffix(".pdf").relative_to(ROOT)),
                folder=tex.parent.name,
            )
        )
    problems.sort(key=lambda p: p["id"])
    return problems


def closure(problems, targets):
    byid = {p["id"]: p for p in problems}
    need, stack = set(), list(targets)
    while stack:
        n = stack.pop()
        if n in need:
            continue
        need.add(n)
        stack.extend(byid[n]["prereqs"] if n != CAPSTONE_ID else [])
    return sorted(need)


if __name__ == "__main__":
    for p in load_problems():
        print(p["nn"], p["title"], p["hours"], p["prereqs"], len(p["deliverables"]), p["n_tasks"])
