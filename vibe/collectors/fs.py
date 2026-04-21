# vibe/collectors/fs.py
import os
from pathlib import Path
from vibe.models import FsInfo, FsNode

_EXCLUDE = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache", "dist", "build"}
_LARGE_LINE_THRESHOLD = 2000
_MAX_READ_SIZE = 1_048_576  # 1 MB — skip reading content for larger files
_MAX_CHILDREN = 200  # cap entries per directory to avoid traversing huge data dirs

def _build_node(path: Path, large_files: list[str], depth: int = 0, max_depth: int = 4) -> FsNode:
    if path.is_file():
        try:
            size = path.stat().st_size
        except Exception:
            size = 0
        try:
            if size <= _MAX_READ_SIZE:
                lines = path.read_text(encoding="utf-8", errors="replace").count("\n")
            else:
                lines = 0
                large_files.append(str(path))
        except Exception:
            lines = 0
        if lines > _LARGE_LINE_THRESHOLD:
            large_files.append(str(path))
        return FsNode(name=path.name, is_dir=False, size_bytes=size, line_count=lines)

    children = []
    if depth < max_depth:
        try:
            entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name))
        except PermissionError:
            entries = []
        count = 0
        for entry in entries:
            if entry.name in _EXCLUDE:
                continue
            if count >= _MAX_CHILDREN:
                break
            children.append(_build_node(entry, large_files, depth + 1, max_depth))
            count += 1

    return FsNode(name=path.name, is_dir=True, children=children)

def collect_fs(path: Path) -> FsInfo:
    large_files: list[str] = []
    tree = _build_node(path, large_files)

    total_files = 0
    stack = [tree]
    while stack:
        node = stack.pop()
        if not node.is_dir:
            total_files += 1
        elif node.children:
            stack.extend(node.children)

    return FsInfo(tree=tree, total_files=total_files, large_files=large_files)
