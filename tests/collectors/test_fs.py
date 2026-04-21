# tests/collectors/test_fs.py
from pathlib import Path
from vibe.collectors.fs import collect_fs

def test_builds_tree(tmp_path):
    (tmp_path / "main.py").write_text("x = 1\n" * 10)
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "helper.py").write_text("y = 2\n")
    info = collect_fs(tmp_path)
    assert info.tree.is_dir
    child_names = [c.name for c in info.tree.children]
    assert "main.py" in child_names
    assert "sub" in child_names

def test_large_file_flagged(tmp_path):
    (tmp_path / "huge.py").write_text("x = 1\n" * 2100)
    info = collect_fs(tmp_path)
    assert any("huge.py" in lf for lf in info.large_files)

def test_excludes_git_dir(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[core]")
    info = collect_fs(tmp_path)
    child_names = [c.name for c in info.tree.children]
    assert ".git" not in child_names
