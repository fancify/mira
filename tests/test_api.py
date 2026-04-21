import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from vibe.main import api

client = TestClient(api)

def make_mock_project(id="test-proj"):
    return {
        "id": id, "name": "Test Project", "path": "/tmp/test",
        "status": "active", "tech_stack": [], "features": [],
        "design_docs": [], "git": None, "plans": None,
        "service": None, "loc": None, "fs": None,
        "deploy": None, "arch_summary": None, "description": None,
    }

def test_get_projects():
    with patch("vibe.main.get_all_projects", return_value=[make_mock_project()]):
        resp = client.get("/api/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-proj"

def test_get_project_by_id():
    with patch("vibe.main.get_all_projects", return_value=[make_mock_project("proj-abc")]):
        resp = client.get("/api/projects/proj-abc")
    assert resp.status_code == 200
    assert resp.json()["id"] == "proj-abc"

def test_get_project_not_found():
    with patch("vibe.main.get_all_projects", return_value=[]):
        resp = client.get("/api/projects/nonexistent")
    assert resp.status_code == 404
