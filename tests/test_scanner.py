import pytest
from pathlib import Path
from vibe.scanner import discover_projects


def test_discovers_git_repos(tmp_path):
    # Create two git repos
    proj_a = tmp_path / "proj_a"
    proj_a.mkdir()
    (proj_a / ".git").mkdir()

    proj_b = tmp_path / "proj_b"
    proj_b.mkdir()
    (proj_b / ".git").mkdir()

    # Non-git dir should be ignored
    (tmp_path / "not_a_repo").mkdir()

    results = discover_projects([str(tmp_path)], exclude=[])
    paths = [r["path"] for r in results]
    assert str(proj_a) in paths
    assert str(proj_b) in paths
    assert len(results) == 2


def test_excludes_dirs(tmp_path):
    node_mod = tmp_path / "node_modules" / "some-pkg"
    node_mod.mkdir(parents=True)
    (node_mod / ".git").mkdir()

    results = discover_projects([str(tmp_path)], exclude=["node_modules"])
    assert len(results) == 0


def test_nested_repos_not_double_counted(tmp_path):
    outer = tmp_path / "outer"
    outer.mkdir()
    (outer / ".git").mkdir()
    # Nested .git should NOT be walked into
    inner = outer / "sub"
    inner.mkdir()
    (inner / ".git").mkdir()

    results = discover_projects([str(tmp_path)], exclude=[])
    # Only outer should be found (we stop recursing into git repos)
    assert len(results) == 1
    assert results[0]["path"] == str(outer)
