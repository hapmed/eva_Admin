import pytest

from app.drivers.simulated import SimulatedDriver
from app.operations import OperationRequest, OperationType, execute, validate_params


def test_validate_accepts_deploy():
    request = OperationRequest(
        type=OperationType.deploy_installation,
        installation_id="i1",
        params={
            "image": "ghcr.io/hapmed/eva-x:1.0.0",
            "name": "eva_alfa",
            "host_port": 9100,
            "container_port": 8000,
            "network": "apps-net",
            "env": {"A": "b"},
            "labels": {"evas.managed_by": "evas-admin"},
        },
    )
    validate_params(request)


def test_validate_accepts_deploy_with_migrate():
    request = OperationRequest(
        type=OperationType.deploy_installation,
        installation_id="i1",
        params={
            "image": "ghcr.io/hapmed/eva-x:1.0.0",
            "name": "eva_alfa",
            "host_port": 9100,
            "migrate": "alembic upgrade head",
        },
    )
    validate_params(request)


def test_validate_rejects_arbitrary_param():
    request = OperationRequest(
        type=OperationType.restart_service,
        installation_id="i1",
        params={"service_name": "web", "image": "evil:latest"},
    )
    with pytest.raises(ValueError):
        validate_params(request)


def test_validate_rejects_missing_param():
    request = OperationRequest(
        type=OperationType.deploy_installation,
        installation_id="i1",
        params={"image": "x:1"},
    )
    with pytest.raises(ValueError):
        validate_params(request)


def test_execute_simulated_deploy():
    request = OperationRequest(
        type=OperationType.deploy_installation,
        installation_id="i1",
        params={"image": "x:1", "name": "n", "host_port": 9100},
    )
    result = execute(request, "simulated")
    assert result.simulated is True
    assert result.status == "accepted"


def test_execute_simulated_remove():
    request = OperationRequest(
        type=OperationType.remove_installation,
        installation_id="i1",
        params={},
    )
    result = execute(request, "simulated")
    assert result.simulated is True
    assert result.data["installation_id"] == "i1"


def test_simulated_driver_mode():
    assert SimulatedDriver().mode == "simulated"
