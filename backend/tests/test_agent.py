from app.agents.client import SimulatedAgent, get_agent


def test_simulated_agent_mode():
    assert SimulatedAgent().mode == "simulated"
    assert get_agent().mode == "simulated"


def test_operations_are_marked_simulated():
    agent = SimulatedAgent()
    assert agent.health_check("inst-1")["simulated"] is True
    assert agent.restart_service("inst-1", "web")["simulated"] is True
    spec = {"image": "x:1.5.0", "name": "n", "host_port": 9100}
    assert agent.upgrade_installation(spec)["simulated"] is True
