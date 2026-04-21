# vibe/collectors/service.py
import re
from pathlib import Path
from typing import Optional
import psutil
from vibe.models import ServiceInfo

# Patterns to scan source code for configured ports
_PORT_RE = re.compile(r'(?:port|PORT)\s*[=:]\s*(\d{3,5})', re.IGNORECASE)
_UVICORN_RE = re.compile(r'uvicorn\.run\([^)]*port\s*=\s*(\d+)')


def _find_project_processes(path: Path) -> list[psutil.Process]:
    """Find running processes whose cwd is inside this project directory."""
    procs = []
    path_str = str(path.resolve())
    for proc in psutil.process_iter(['pid', 'name', 'cwd', 'cmdline']):
        try:
            cwd = proc.info.get('cwd') or ''
            if cwd and (cwd == path_str or cwd.startswith(path_str + '/')):
                procs.append(proc)
                continue
            # Also match by cmdline containing the project path
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if path_str in cmdline:
                procs.append(proc)
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            continue
    return procs


def _get_listening_ports(proc: psutil.Process) -> list[int]:
    """Get ports this process is listening on."""
    ports = []
    try:
        for conn in (proc.connections(kind='inet') or []):
            if conn.status == 'LISTEN' and hasattr(conn.laddr, 'port'):
                ports.append(conn.laddr.port)
    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
        pass
    return ports


def _scan_code_for_port(path: Path) -> Optional[int]:
    """Scan source files for a configured port number."""
    candidates = []
    # Check common entry points first
    for name in ['main.py', 'app.py', 'server.py', 'run.py', 'manage.py',
                 'index.js', 'server.js', 'app.js']:
        f = path / name
        if f.exists():
            try:
                text = f.read_text(encoding='utf-8', errors='replace')
                for m in _UVICORN_RE.finditer(text):
                    candidates.append(int(m.group(1)))
                for m in _PORT_RE.finditer(text):
                    p = int(m.group(1))
                    if 1024 <= p <= 65535:
                        candidates.append(p)
            except Exception:
                pass
    # Check .env
    env_file = path / '.env'
    if env_file.exists():
        try:
            for m in _PORT_RE.finditer(env_file.read_text(encoding='utf-8', errors='replace')):
                p = int(m.group(1))
                if 1024 <= p <= 65535:
                    candidates.append(p)
        except Exception:
            pass
    return candidates[0] if candidates else None


def collect_service(path: Path, vibe_cfg: Optional[dict]) -> ServiceInfo:
    # 1. Prefer explicit vibe.yaml config
    cfg_port = None
    cfg_process = None
    deploy_url = None
    if vibe_cfg:
        svc = vibe_cfg.get('service', {})
        cfg_port = svc.get('port')
        cfg_process = svc.get('process')
        deploy_url = vibe_cfg.get('deploy', {}).get('url')

    # 2. Auto-detect running processes for this project
    procs = _find_project_processes(path)
    detected_port = None
    detected_name = None
    is_running = False

    if procs:
        is_running = True
        detected_name = procs[0].name()
        for proc in procs:
            ports = _get_listening_ports(proc)
            if ports:
                detected_port = ports[0]
                break

    # 3. Fall back to code scan for port (useful even when not running)
    code_port = _scan_code_for_port(path) if not detected_port and not cfg_port else None

    port = cfg_port or detected_port or code_port
    process_name = cfg_process or detected_name

    # 4. If we have a port from config but no running process, check the port
    if not is_running and port:
        try:
            for proc in psutil.process_iter(['connections']):
                try:
                    for conn in (proc.info.get('connections') or []):
                        if hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                            is_running = True
                            break
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
                if is_running:
                    break
        except Exception:
            pass

    return ServiceInfo(
        port=port,
        process_name=process_name,
        is_running=is_running,
        url=deploy_url,
    )
