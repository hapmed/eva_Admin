"""Esquemas de monitoreo y alertas."""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthCheckOut(BaseModel):
    status: str
    checked_at: datetime | None


class ServiceHealthOut(BaseModel):
    service_name: str
    status: str
    health_status: str
    last_checked_at: datetime | None


class LogsOut(BaseModel):
    simulated: bool
    lines: list[str]
    retention_note: str


class MetricSample(BaseModel):
    metric_type: str
    value: float
    captured_at: datetime


class MetricsOut(BaseModel):
    simulated: bool
    samples: list[MetricSample]


class AlertOut(BaseModel):
    key: str
    type: str
    severity: str
    entity_type: str
    entity_id: str
    message: str
    status: str


class AlertAction(BaseModel):
    key: str = Field(min_length=1, max_length=200)
