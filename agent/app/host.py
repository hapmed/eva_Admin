"""Métricas del servidor (lectura de /proc y del sistema de archivos del host).

El agente monta `/proc` y `/` del host en solo lectura (`/host/proc`, `/host`).
Devuelve valores "instantáneos"; CPU y red se calculan por diferencia entre
llamadas (se guarda la muestra anterior en memoria).
"""

import os
import shutil
import time

from app.config import get_settings

_prev_cpu: tuple[float, float] | None = None  # (total, idle)
_prev_net: tuple[float, float, float] | None = None  # (rx, tx, ts)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def _proc(name: str) -> str:
    return os.path.join(get_settings().host_proc, name)


def _cpu_times() -> tuple[float, float]:
    line = _read(_proc("stat")).splitlines()[0] if _read(_proc("stat")) else ""
    parts = line.split()[1:] if line else []
    numbers = [float(value) for value in parts] if parts else [0.0]
    idle = numbers[3] + (numbers[4] if len(numbers) > 4 else 0.0)
    return sum(numbers), idle


def _cpu_percent() -> float:
    global _prev_cpu
    total, idle = _cpu_times()
    prev = _prev_cpu
    if prev is None or total <= prev[0]:
        time.sleep(0.1)
        total2, idle2 = _cpu_times()
        delta_total = total2 - total
        delta_idle2 = idle2 - idle
        _prev_cpu = (total2, idle2)
        if delta_total <= 0:
            return 0.0
        return round((1 - delta_idle2 / delta_total) * 100, 1)
    delta_total = total - prev[0]
    delta_idle = idle - prev[1]
    _prev_cpu = (total, idle)
    if delta_total <= 0:
        return 0.0
    return round((1 - delta_idle / delta_total) * 100, 1)


def _meminfo() -> dict[str, float]:
    values: dict[str, float] = {}
    for line in _read(_proc("meminfo")).splitlines():
        if ":" in line:
            key, raw = line.split(":", 1)
            parts = raw.strip().split()
            if parts:
                values[key.strip()] = float(parts[0]) * 1024  # kB -> bytes
    total = values.get("MemTotal", 0.0)
    available = values.get("MemAvailable", values.get("MemFree", 0.0))
    used = max(total - available, 0.0)
    percent = round(used / total * 100, 1) if total else 0.0
    return {"total": total, "used": used, "percent": percent}


def _disk() -> dict[str, float]:
    try:
        usage = shutil.disk_usage(get_settings().host_root)
    except OSError:
        return {"total": 0.0, "used": 0.0, "percent": 0.0}
    percent = round(usage.used / usage.total * 100, 1) if usage.total else 0.0
    return {"total": float(usage.total), "used": float(usage.used), "percent": percent}


def _net() -> dict[str, float]:
    global _prev_net
    rx = tx = 0.0
    for line in _read(_proc("net/dev")).splitlines():
        if ":" not in line or line.strip().startswith(("lo:", "Inter-", "face")):
            continue
        iface, data = line.split(":", 1)
        if iface.strip() == "lo":
            continue
        fields = data.split()
        if len(fields) >= 9:
            rx += float(fields[0])
            tx += float(fields[8])
    now = time.time()
    rx_rate = tx_rate = 0.0
    if _prev_net is not None:
        prev_rx, prev_tx, prev_ts = _prev_net
        dt = now - prev_ts
        if dt > 0:
            rx_rate = max((rx - prev_rx) / dt, 0.0)
            tx_rate = max((tx - prev_tx) / dt, 0.0)
    _prev_net = (rx, tx, now)
    return {
        "rx_bytes": rx,
        "tx_bytes": tx,
        "rx_rate": round(rx_rate, 1),
        "tx_rate": round(tx_rate, 1),
    }


def _load_uptime() -> tuple[float, float, float, float]:
    load_parts = _read(_proc("loadavg")).split()
    loads = [float(value) for value in load_parts[:3]] if len(load_parts) >= 3 else [0.0, 0.0, 0.0]
    uptime_parts = _read(_proc("uptime")).split()
    uptime = float(uptime_parts[0]) if uptime_parts else 0.0
    return loads[0], loads[1], loads[2], uptime


def _cpu_count() -> int:
    return max(_read(_proc("cpuinfo")).count("processor"), 1)


def host_stats() -> dict:
    mem = _meminfo()
    disk = _disk()
    net = _net()
    load1, load5, load15, uptime = _load_uptime()
    return {
        "simulated": False,
        "cpu_percent": _cpu_percent(),
        "cpu_count": _cpu_count(),
        "mem_total": mem["total"],
        "mem_used": mem["used"],
        "mem_percent": mem["percent"],
        "disk_total": disk["total"],
        "disk_used": disk["used"],
        "disk_percent": disk["percent"],
        "load1": load1,
        "load5": load5,
        "load15": load15,
        "uptime_seconds": uptime,
        "net_rx_bytes": net["rx_bytes"],
        "net_tx_bytes": net["tx_bytes"],
        "net_rx_rate": net["rx_rate"],
        "net_tx_rate": net["tx_rate"],
    }
