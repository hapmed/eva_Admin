"""Esquema de métricas del servidor."""

from pydantic import BaseModel


class SystemStats(BaseModel):
    simulated: bool
    cpu_percent: float
    cpu_count: int
    mem_total: float
    mem_used: float
    mem_percent: float
    disk_total: float
    disk_used: float
    disk_percent: float
    load1: float
    load5: float
    load15: float
    uptime_seconds: float
    net_rx_bytes: float
    net_tx_bytes: float
    net_rx_rate: float
    net_tx_rate: float
