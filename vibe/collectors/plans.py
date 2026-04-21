# vibe/collectors/plans.py
import re
from pathlib import Path
from vibe.models import PlanInfo, PlanFile, PlanTask

_DONE_RE = re.compile(r"^\s*-\s*\[x\]\s+(.+)", re.IGNORECASE)
_TODO_RE = re.compile(r"^\s*-\s*\[ \]\s+(.+)")

# Common root-level task/plan file names to scan when docs/superpowers/plans/ doesn't exist
_ROOT_PLAN_FILES = ["TASKS.md", "TODO.md", "PROGRESS.md", "PLAN.md", "ROADMAP.md"]

def _candidate_files(path: Path) -> list[Path]:
    """Return plan files to scan, in priority order."""
    superpowers = path / "docs" / "superpowers" / "plans"
    if superpowers.exists():
        return sorted(superpowers.glob("*.md"))
    # Fall back: root-level task files + docs/*.md that contain checkboxes
    candidates = []
    for name in _ROOT_PLAN_FILES:
        f = path / name
        if f.exists():
            candidates.append(f)
    # docs/ top-level md files (not subdirs)
    docs_dir = path / "docs"
    if docs_dir.exists():
        for f in sorted(docs_dir.glob("*.md")):
            candidates.append(f)
    return candidates

def collect_plans(path: Path) -> PlanInfo:
    plan_files = []
    total = 0
    done = 0

    for md_file in _candidate_files(path):
        tasks = []
        for line in md_file.read_text(encoding="utf-8", errors="replace").splitlines():
            m_done = _DONE_RE.match(line)
            m_todo = _TODO_RE.match(line)
            if m_done:
                tasks.append(PlanTask(text=m_done.group(1).strip(), done=True))
            elif m_todo:
                tasks.append(PlanTask(text=m_todo.group(1).strip(), done=False))
        if tasks:
            plan_files.append(PlanFile(filename=md_file.name, tasks=tasks))
            total += len(tasks)
            done += sum(1 for t in tasks if t.done)

    return PlanInfo(files=plan_files, total=total, done=done)

