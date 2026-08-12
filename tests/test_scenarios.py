from app.config import ASSESSMENT_NUMBER
from app.scenario_store import load_scenarios


def test_exactly_ten_scenarios():
    scenarios = load_scenarios()
    assert len(scenarios) == 10
    assert len({s["id"] for s in scenarios}) == 10


def test_every_scenario_has_required_fields():
    required = {"id", "title", "persona", "goal", "opening_line", "edge_behavior"}
    for scenario in load_scenarios():
        assert required <= scenario.keys()
        assert all(str(scenario[key]).strip() for key in required)


def test_assessment_number_is_hardcoded_safely():
    assert ASSESSMENT_NUMBER == "+18054398008"
