"""Cloudflare: alta de DNS (CNAME al túnel) y regla de ingress del túnel.

Publica el dominio del cliente apuntando a `http://localhost:<puerto>` (donde
cloudflared corre en el host y alcanza el contenedor publicado en 127.0.0.1).
"""

from typing import Any

import httpx

from app.core.config import get_settings

_API = "https://api.cloudflare.com/client/v4"


def _configured() -> bool:
    settings = get_settings()
    return bool(
        settings.cloudflare_api_token
        and settings.cloudflare_account_id
        and settings.cloudflare_zone_id
        and settings.cloudflare_tunnel_id
    )


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_settings().cloudflare_api_token}",
        "Content-Type": "application/json",
    }


def fqdn(subdomain: str) -> str:
    settings = get_settings()
    return subdomain if "." in subdomain else f"{subdomain}.{settings.public_domain_suffix}"


def upsert_hostname(subdomain: str, host_port: int) -> dict[str, Any]:
    if not _configured():
        raise RuntimeError("Cloudflare no configurado")
    settings = get_settings()
    hostname = fqdn(subdomain)
    target = f"{settings.cloudflare_tunnel_id}.cfargotunnel.com"

    with httpx.Client(timeout=30) as client:
        # 1) DNS CNAME -> túnel (proxied)
        existing = (
            client.get(
                f"{_API}/zones/{settings.cloudflare_zone_id}/dns_records",
                params={"name": hostname},
                headers=_headers(),
            )
            .json()
            .get("result", [])
        )
        record = {
            "type": "CNAME",
            "name": hostname,
            "content": target,
            "proxied": True,
        }
        if existing:
            client.put(
                f"{_API}/zones/{settings.cloudflare_zone_id}/dns_records/{existing[0]['id']}",
                json=record,
                headers=_headers(),
            )
        else:
            client.post(
                f"{_API}/zones/{settings.cloudflare_zone_id}/dns_records",
                json=record,
                headers=_headers(),
            )

        # 2) Ingress del túnel (insertar antes del catch-all)
        config = client.get(
            f"{_API}/accounts/{settings.cloudflare_account_id}/cfd_tunnel/"
            f"{settings.cloudflare_tunnel_id}/configurations",
            headers=_headers(),
        ).json()["result"]["config"]
        ingress = [rule for rule in config.get("ingress", []) if rule.get("hostname") != hostname]
        catch_all = [rule for rule in ingress if not rule.get("hostname")]
        named = [rule for rule in ingress if rule.get("hostname")]
        named.append({"hostname": hostname, "service": f"http://localhost:{host_port}"})
        named.extend(catch_all or [{"service": "http_status:404"}])
        client.put(
            f"{_API}/accounts/{settings.cloudflare_account_id}/cfd_tunnel/"
            f"{settings.cloudflare_tunnel_id}/configurations",
            json={"config": {"ingress": named}},
            headers=_headers(),
        )

    return {"hostname": hostname, "host_port": host_port, "target": target}
