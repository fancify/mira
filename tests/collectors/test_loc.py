# tests/collectors/test_loc.py
import pytest
from pathlib import Path
from vibe.collectors.loc import collect_loc

def test_count_python_files(tmp_path):
    (tmp_path / "main.py").write_text("# comment\nprint('hello')\n\n")
    info = collect_loc(tmp_path)
    assert info.file_count >= 1
    assert info.total_lines >= 3
    assert info.code_lines >= 1

def test_excludes_ignored_dirs(tmp_path):
    node_mod = tmp_path / "node_modules"
    node_mod.mkdir()
    (node_mod / "big.js").write_text("x = 1\n" * 1000)
    (tmp_path / "main.py").write_text("print('hi')\n")
    info = collect_loc(tmp_path)
    # node_modules should be excluded
    assert info.total_lines < 100

def test_empty_dir(tmp_path):
    info = collect_loc(tmp_path)
    assert info.total_lines == 0
    assert info.file_count == 0
