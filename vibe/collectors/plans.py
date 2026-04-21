# vibe/collectors/plans.py
import re
from pathlib import Path
from vibe.models import PlanInfo, PlanFile, PlanTask

_DONE_RE = re.compile(r"^\s*-\s*\[x\]\s+(.+)", re.IGNORECASE)
_TODO_RE = re.compile(r"^\s*-\s*\[ \]\s+(.+)")

def collect_plans(path: Path) -> PlanInfo:
    plans_dir = path / "docs" / "superpowers" / "plans"
    if not plans_dir.exists():
        return PlanInfo(files=[], total=0, done=0)

    plan_files = []
    total = 0
    done = 0

    for md_file in sorted(plans_dir.glob("*.md")):
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
