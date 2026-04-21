# vibe/collectors/loc.py
import subprocess
import os
from pathlib import Path
from vibe.models import LocInfo, LocLanguage

_EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache", "dist", "build"}
_CODE_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".jsx": "JavaScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".html": "HTML",
    ".css": "CSS", ".sh": "Shell", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".json": "JSON", ".md": "Markdown",
}

def _pure_python_count(path: Path) -> LocInfo:
    lang_data: dict[str, dict] = {}
    total_lines = code_lines = comment_lines = blank_lines = 0
    file_count = 0

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in _CODE_EXTENSIONS:
                continue
            lang = _CODE_EXTENSIONS[ext]
            fpath = Path(root) / fname
            try:
                lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue

            file_count += 1
            f_total = len(lines)
            f_blank = sum(1 for l in lines if not l.strip())
            f_comment = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*", "<!--")))
            f_code = f_total - f_blank - f_comment

            total_lines += f_total
            blank_lines += f_blank
            comment_lines += f_comment
            code_lines += f_code

            ld = lang_data.setdefault(lang, {"files": 0, "code": 0, "comment": 0, "blank": 0})
            ld["files"] += 1
            ld["code"] += f_code
            ld["comment"] += f_comment
            ld["blank"] += f_blank

    languages = [
        LocLanguage(name=name, files=d["files"], code=d["code"],
                    comment=d["comment"], blank=d["blank"])
        for name, d in sorted(lang_data.items(), key=lambda x: -x[1]["code"])
    ]
    return LocInfo(
        total_lines=total_lines, code_lines=code_lines,
        comment_lines=comment_lines, blank_lines=blank_lines,
        file_count=file_count, languages=languages,
    )

def collect_loc(path: Path) -> LocInfo:
    # Try cloc first; fall back to pure Python
    try:
        result = subprocess.run(
            ["cloc", "--json", "--quiet", str(path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            import json
            data = json.loads(result.stdout)
            languages = []
            for lang, vals in data.items():
                if lang in ("header", "SUM"):
                    continue
                languages.append(LocLanguage(
                    name=lang, files=vals.get("nFiles", 0),
                    code=vals.get("code", 0), comment=vals.get("comment", 0),
                    blank=vals.get("blank", 0),
                ))
            summ = data.get("SUM", {})
            return LocInfo(
                total_lines=summ.get("code", 0) + summ.get("comment", 0) + summ.get("blank", 0),
                code_lines=summ.get("code", 0),
                comment_lines=summ.get("comment", 0),
                blank_lines=summ.get("blank", 0),
                file_count=summ.get("nFiles", 0),
                languages=languages,
            )
    except Exception:
        pass
    return _pure_python_count(path)
