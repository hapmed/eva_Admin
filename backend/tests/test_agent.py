from app.agents.client import SimulatedAgent, get_agent


def test_simulated_agent_mode():
    assert SimulatedAgent().mode == "simulated"
    assert get_agent().mode == "simulated"


def test_operations_are_marked_simulated():
    agent = SimulatedAgent()
    assert agent.health_check("inst-1")["simulated"] is True
    assert agent.restart_service("inst-1", "web")["simulated"] is True
    assert agent.upgrade_installation("inst-1", "1.5.0")["simulated"] is True
