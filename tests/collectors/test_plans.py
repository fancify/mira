# tests/collectors/test_plans.py
import pytest
from pathlib import Path
from vibe.collectors.plans import collect_plans

def test_no_plans_dir(tmp_path):
    info = collect_plans(tmp_path)
    assert info.total == 0
    assert info.done == 0
    assert info.files == []

def test_parses_checkboxes(tmp_path):
    plans_dir = tmp_path / "docs" / "superpowers" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-01-01-feature.md").write_text(
        "# Feature\n- [x] done task\n- [ ] pending task\n- [x] another done\n"
    )
    info = collect_plans(tmp_path)
    assert info.total == 3
    assert info.done == 2
    assert len(info.files) == 1
    assert info.files[0].filename == "2026-01-01-feature.md"

def test_multiple_plan_files(tmp_path):
    plans_dir = tmp_path / "docs" / "superpowers" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "plan-a.md").write_text("- [x] task1\n")
    (plans_dir / "plan-b.md").write_text("- [ ] task2\n- [ ] task3\n")
    info = collect_plans(tmp_path)
    assert info.total == 3
    assert info.done == 1
