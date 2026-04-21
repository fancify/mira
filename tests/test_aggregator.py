import subprocess
import pytest
from pathlib import Path
from vibe.aggregator import collect_project, extract_tech_stack, extract_arch_summary


@pytest.fixture
def git_repo(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True)
    (tmp_path / "README.md").write_text("# Proj\n## 架构\nFastAPI + SQLite\n## Other\nstuff")
    (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi>=0.110"]\n')
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
    return tmp_path


def test_collect_project_returns_project_info(git_repo):
    info = collect_project(git_repo, name="Test", vibe_cfg=None)
    assert info.id == git_repo.name
    assert info.name == "Test"
    assert info.git is not None
    assert info.plans is not None


def test_extract_tech_stack_from_pyproject(git_repo):
    stack = extract_tech_stack(git_repo)
    names = [t.name for t in stack]
    assert "fastapi" in names


def test_extract_arch_summary(git_repo):
    summary = extract_arch_summary(git_repo)
    assert "FastAPI" in summary
