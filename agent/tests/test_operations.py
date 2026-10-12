import pytest

from app.drivers.simulated import SimulatedDriver
from app.operations import OperationRequest, OperationType, execute, validate_params


def test_validate_accepts_deploy_with_domain():
    request = OperationRequest(
        type=OperationType.deploy_installation,
        installation_id="i1",
        params={"eva_version": "1.0.0", "domain": "x.test"},
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
        type=OperationType.upgrade_installation, installation_id="i1", params={}
    )
    with pytest.raises(ValueError):
        validate_params(request)


def test_execute_simulated_marks_result():
    request = OperationRequest(type=OperationType.health_check, installation_id="i1")
    result = execute(request, "simulated")
    assert result.simulated is True
    assert result.status == "accepted"


def test_simulated_driver_mode():
    assert SimulatedDriver().mode == "simulated"
