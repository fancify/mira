# vibe/collectors/deploy.py
import re
import socket
from pathlib import Path
from typing import Optional
from vibe.models import DeployInfo

# Match both `VAR="value"` and `VAR="${VAR:-value}"` shell patterns
_HOST_RE = re.compile(r'REMOTE_HOST[^=\n]*=["\'${]*(?:\w+:-)?([0-9a-zA-Z][\w.\-]*)')
_USER_RE = re.compile(r'REMOTE_USER[^=\n]*=["\'${]*(?:\w+:-)?([0-9a-zA-Z][\w.\-]*)')
_DIR_RE  = re.compile(r'REMOTE_DIR[^=\n]*=["\'${]*(?:\w+:-)?(/[\w./\-]+)')
_SSH_RE  = re.compile(r'ssh\s+\S+\s+([\w.\-]+@)([\w.\-]+)')


def _infer_cloud(host: str) -> str:
    """Try to infer cloud provider from hostname or reverse DNS."""
    if not host:
        return "vps"
    lower = host.lower()
    if any(k in lower for k in ["amazonaws.com", "compute.aws", "ec2"]):
        return "ec2"
    if any(k in lower for k in ["compute.googleapis.com", "gcp", "googlecloud"]):
        return "gcp"
    if any(k in lower for k in ["cloudapp.azure.com", "azure", "windows.net"]):
        return "azure"
    if any(k in lower for k in ["lightsail"]):
        return "lightsail"
    # Try reverse DNS if it looks like an IP
    ip_re = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
    if ip_re.match(host):
        try:
            rdns = socket.gethostbyaddr(host)[0]
            return _infer_cloud(rdns)
        except Exception:
            pass
    return "vps"


def _scan_sh_for_deploy(path: Path) -> Optional[dict]:
    """Scan shell scripts for SSH/rsync deploy patterns."""
    for sh in sorted(path.rglob("*.sh")):
        if any(p in str(sh) for p in ["node_modules", ".git", ".venv", "venv"]):
            continue
        try:
            text = sh.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "rsync" not in text and "ssh" not in text:
            continue
        host = (m := _HOST_RE.search(text)) and m.group(1)
        user = (m := _USER_RE.search(text)) and m.group(1)
        rdir = (m := _DIR_RE.search(text)) and m.group(1)
        if host and host not in ("localhost", "127.0.0.1"):
            return {"host": host, "user": user or "root", "remote_dir": rdir,
                    "cmd": str(sh.relative_to(path))}
        # fallback: parse ssh user@host pattern
        m = _SSH_RE.search(text)
        if m:
            user_part = m.group(1).rstrip("@")
            h = m.group(2)
            if h not in ("localhost", "127.0.0.1"):
                return {"host": h, "user": user_part, "remote_dir": rdir,
                        "cmd": str(sh.relative_to(path))}
    return None


def _scan_makefile(path: Path) -> Optional[dict]:
    makefile = path / "Makefile"
    if not makefile.exists():
        return None
    try:
        text = makefile.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    host = (m := _HOST_RE.search(text)) and m.group(1)
    if host and host not in ("localhost", "127.0.0.1"):
        user = (m := _USER_RE.search(text)) and m.group(1)
        rdir = (m := _DIR_RE.search(text)) and m.group(1)
        return {"host": host, "user": user or None, "remote_dir": rdir, "cmd": "make deploy"}
    return None


def collect_deploy(path: Path, vibe_cfg: Optional[dict]) -> DeployInfo:
    # 1. Explicit vibe.yaml config takes priority
    if vibe_cfg and "deploy" in vibe_cfg:
        d = vibe_cfg["deploy"]
        return DeployInfo(
            type=d.get("type", "none"),
            host=d.get("host"),
            user=d.get("user"),
            remote_dir=d.get("remote_dir"),
            process=d.get("process"),
            url=d.get("url"),
            cmd=d.get("cmd"),
        )

    # 2. Detect well-known PaaS config files
    paas_files = [
        ("netlify.toml", "netlify"),
        ("vercel.json", "vercel"),
        (".vercel", "vercel"),
        ("railway.json", "railway"),
        ("render.yaml", "render"),
        ("render.yml", "render"),
        ("Procfile", "heroku"),
        ("app.yaml", "gae"),          # Google App Engine
        ("appspec.yml", "codedeploy"),  # AWS CodeDeploy
    ]
    for filename, platform in paas_files:
        if (path / filename).exists():
            url = None
            # Try to read site URL from netlify/vercel config
            if platform == "netlify":
                try:
                    import tomllib
                except ImportError:
                    try:
                        import tomli as tomllib  # type: ignore
                    except ImportError:
                        tomllib = None
                # netlify doesn't usually have site URL in toml, skip
            return DeployInfo(type=platform)

    # 3. Docker / docker-compose
    if (path / "docker-compose.yml").exists() or (path / "docker-compose.yaml").exists():
        return DeployInfo(type="docker")
    if (path / "Dockerfile").exists():
        return DeployInfo(type="docker")

    # 4. Scan shell scripts for SSH/rsync deploy
    ssh_info = _scan_sh_for_deploy(path) or _scan_makefile(path)
    if ssh_info:
        cloud_type = _infer_cloud(ssh_info["host"])
        return DeployInfo(
            type=cloud_type,
            host=ssh_info["host"],
            user=ssh_info.get("user"),
            remote_dir=ssh_info.get("remote_dir"),
            cmd=ssh_info.get("cmd"),
        )

    # 5. Scan GitHub Actions for cloud deploy hints
    workflows_dir = path / ".github" / "workflows"
    if workflows_dir.exists():
        for wf in workflows_dir.glob("*.yml"):
            try:
                text = wf.read_text(encoding="utf-8", errors="replace").lower()
            except Exception:
                continue
            if "aws" in text or "ec2" in text or "lightsail" in text:
                return DeployInfo(type="ec2")
            if "gcp" in text or "google" in text or "gke" in text:
                return DeployInfo(type="gcp")
            if "azure" in text:
                return DeployInfo(type="azure")
            if "heroku" in text:
                return DeployInfo(type="heroku")
            if "vercel" in text:
                return DeployInfo(type="vercel")
            if "netlify" in text:
                return DeployInfo(type="netlify")

    return DeployInfo(type="none")
