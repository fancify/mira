import logging
import re
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_monitored: dict[str, dict] = {}
_terminal_alerts: list[dict] = []
_monitor_lock = threading.Lock()

_AUTO_COMMANDS = {"claude", "ccc"}
_AUTO_TITLE_FRAGMENTS = {"Claude Code"}
_CLAUDE_TITLE_ICONS = {"✳", "⠐", "⠂", "⠈", "⠁", "⠑", "⠃", "⠊", "⠔", "⠤", "⠠"}  # Claude Code spinner chars
_CODEX_COMMANDS = {"codex"}
_CODEX_TITLE_FRAGMENTS = {"Codex"}

WAIT_PATTERNS = [
    r"do you want to",
    r"\(y/n\)",
    r"\[y/n\]",
    r"\ballow\b",
    r"\bdeny\b",
    r"continue\?",
    r"proceed\?",
    r"press enter",
    r"are you sure",
]
_WAIT_RE = re.compile("|".join(WAIT_PATTERNS), re.IGNORECASE)


def register_pane(target: str, label: str, project_id: str | None = None) -> None:
    with _monitor_lock:
        if target not in _monitored:
            _monitored[target] = {
                "target": target,
                "label": label,
                "command": "",
                "cwd": "",
                "auto": False,
                "project_id": project_id,
                "last_output": "",
                "waiting": False,
                "registered_at": time.time(),
            }


def unregister_pane(target: str) -> None:
    with _monitor_lock:
        _monitored.pop(target, None)


def get_panes() -> list[dict]:
    with _monitor_lock:
        return [dict(v) for v in _monitored.values()]


def get_terminal_alerts() -> list[dict]:
    with _monitor_lock:
        alerts = list(_terminal_alerts)
        _terminal_alerts.clear()
    return alerts


_projects_cache: list[dict] = []
_projects_cache_ts: float = 0.0
_PROJECTS_CACHE_TTL: float = 60.0


def _get_projects() -> list[dict]:
    """Return cached project list, refreshing at most once per 60 seconds."""
    global _projects_cache, _projects_cache_ts
    now = time.time()
    if _projects_cache and now - _projects_cache_ts < _PROJECTS_CACHE_TTL:
        return _projects_cache
    try:
        from vibe.config import load_global_config
        from vibe.scanner import discover_projects
        cfg = load_global_config()
        _projects_cache = discover_projects(
            cfg["scan_dirs"], cfg["exclude"],
            cfg.get("extra_projects"), cfg.get("excluded_paths"),
        )
        _projects_cache_ts = now
    except Exception:
        pass
    return _projects_cache


def _match_project(cwd: str) -> str | None:
    """Match a cwd to a known Mira project path."""
    try:
        for p in _get_projects():
            if cwd.startswith(p["path"]):
                return Path(p["path"]).name
    except Exception:
        pass
    return None


def _poll_once() -> None:
    from vibe.tmux_bridge import list_panes, capture_pane

    # Auto-discover Claude panes
    try:
        all_panes = list_panes()
    except Exception as e:
        logger.warning("list_panes failed: %s", e)
        all_panes = []

    # Snapshot currently tracked targets to avoid calling _match_project for known panes
    with _monitor_lock:
        tracked_targets = set(_monitored.keys())

    # Auto-discover Claude / Codex panes — compute project_id OUTSIDE the lock (I/O)
    new_entries = {}
    for pane in all_panes:
        title = pane.get("title", "")
        is_claude = pane["command"] in _AUTO_COMMANDS or any(
            frag in title for frag in _AUTO_TITLE_FRAGMENTS
        ) or (title and title[0] in _CLAUDE_TITLE_ICONS)
        is_codex = not is_claude and (
            pane["command"] in _CODEX_COMMANDS or any(
                frag in title for frag in _CODEX_TITLE_FRAGMENTS
            )
        )
        # For unrecognized node panes not yet tracked, check terminal output for Codex
        # Codex uses alternate screen, so check both scrollback and visible pane
        if not is_claude and not is_codex and pane["target"] not in tracked_targets:
            _codex_markers = ("OpenAI Codex", "codex app", "gpt-5.4 ", "gpt-5.3 ", "gpt-4o ")
            for cap_args in [
                ["-p"],               # visible (alternate screen)
                ["-p", "-S", "-50"],  # scrollback
            ]:
                try:
                    import subprocess as _sp
                    proc = _sp.run(
                        ["tmux", "capture-pane", "-t", pane["target"]] + cap_args,
                        capture_output=True, text=True, timeout=3,
                    )
                    if proc.returncode == 0 and any(m in proc.stdout for m in _codex_markers):
                        is_codex = True
                        break
                except Exception:
                    pass
        if is_claude or is_codex:
            project_id = (
                None if pane["target"] in tracked_targets
                else _match_project(pane["cwd"])
            )
            display_cmd = "codex" if is_codex else "claude"
            new_entries[pane["target"]] = (pane, project_id, display_cmd)

    with _monitor_lock:
        for target, (pane, project_id, display_cmd) in new_entries.items():
            if target not in _monitored:
                _monitored[target] = {
                    "target": pane["target"],
                    "label": f"{display_cmd}/{Path(pane['cwd']).name}",
                    "command": display_cmd,
                    "cwd": pane["cwd"],
                    "auto": True,
                    "project_id": project_id,
                    "last_output": "",
                    "waiting": False,
                    "registered_at": time.time(),
                }
        # Evict any pane whose tmux target no longer exists
        current_targets = set(p["target"] for p in all_panes)
        stale = [t for t in _monitored if t not in current_targets]
        for t in stale:
            del _monitored[t]
        targets = list(_monitored.keys())

    for target in targets:
        try:
            output = capture_pane(target, lines=20)
        except RuntimeError:
            with _monitor_lock:
                _monitored.pop(target, None)
            continue

        last_10_lines = "\n".join(output.splitlines()[-10:])
        is_waiting = bool(_WAIT_RE.search(last_10_lines))

        with _monitor_lock:
            if target not in _monitored:
                continue
            entry = _monitored[target]
            was_waiting = entry["waiting"]
            entry["last_output"] = output
            entry["waiting"] = is_waiting

            if is_waiting and not was_waiting:
                snippet = last_10_lines.strip()[-200:]
                _terminal_alerts.append({
                    "target": target,
                    "label": entry["label"],
                    "snippet": snippet,
                    "ts": int(time.time() * 1000),
                })


def run_monitor() -> None:
    """Infinite poll loop. Runs as a daemon thread."""
    logger.info("Terminal monitor started")
    while True:
        try:
            _poll_once()
        except Exception as e:
            logger.warning("Terminal monitor poll error: %s", e)
        time.sleep(2)
