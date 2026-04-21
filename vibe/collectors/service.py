# vibe/collectors/service.py
from pathlib import Path
from typing import Optional
import psutil
from vibe.models import ServiceInfo

def collect_service(path: Path, vibe_cfg: Optional[dict]) -> ServiceInfo:
    if not vibe_cfg or "service" not in vibe_cfg:
        return ServiceInfo()

    svc = vibe_cfg["service"]
    port = svc.get("port")
    process_name = svc.get("process")
    deploy_url = vibe_cfg.get("deploy", {}).get("url")

    is_running = False
    if port:
        try:
            conns = psutil.net_connections()
            is_running = any(
                hasattr(c.laddr, "port") and c.laddr.port == port
                for c in conns
            )
        except (psutil.AccessDenied, Exception):
            is_running = False

    return ServiceInfo(
        port=port,
        process_name=process_name,
        is_running=is_running,
        url=deploy_url,
    )
