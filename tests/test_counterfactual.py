"""Counterfactual uses only initiation fields. Changing actuals does not change expectation."""

from __future__ import annotations

from shadowlock.counterfactual import Expectation
from shadowlock.envelope import JobEnvelope
from shadowlock.ledger import FinancialLedger

PRIORS = {
    "install": {
        "duration": (20.0, 80.0),
        "cost": (50.0, 150.0),
        "revenue": (100.0, 400.0),
    }
}


def test_expectation_ignores_actuals() -> None:
    kwargs = dict(
        task_class="install",
        urgency=0.4,
        context_signals={"region": "north"},
        history=[],
        class_priors=PRIORS,
    )
    e1 = Expectation.compute(**kwargs)
    e2 = Expectation.compute(**kwargs)
    assert e1 == e2
    # Actuals are not even accepted by compute(); feeding different actuals
    # through the ledger changes only the delta.
    env_a = JobEnvelope(
        hashed_id="aa",
        timestamp="2026-07-01T00:00:00Z",
        task_class="install",
        urgency=0.4,
        context_signals={"region": "north"},
        actual_revenue=50.0,
        actual_cost=200.0,
        actual_duration=90.0,
    )
    env_b = JobEnvelope(
        hashed_id="bb",
        timestamp="2026-07-01T00:00:00Z",
        task_class="install",
        urgency=0.4,
        context_signals={"region": "north"},
        actual_revenue=900.0,
        actual_cost=10.0,
        actual_duration=10.0,
    )
    led_a = FinancialLedger()
    led_b = FinancialLedger()
    led_a.add(env_a, e1)
    led_b.add(env_b, e1)
    assert led_a.money_made != led_b.money_made or led_a.money_lost != led_b.money_lost
    # same expectation object / values
    assert e1.revenue == e2.revenue
    assert e1.cost == e2.cost
    assert e1.duration == e2.duration


def test_history_is_class_conditional_only() -> None:
    history = [
        {"task_class": "install", "actual_duration": 10.0, "actual_cost": 10.0, "actual_revenue": 10.0},
        {"task_class": "install", "actual_duration": 30.0, "actual_cost": 30.0, "actual_revenue": 30.0},
        {"task_class": "repair", "actual_duration": 999.0, "actual_cost": 999.0, "actual_revenue": 999.0},
    ]
    exp = Expectation.compute(
        task_class="install",
        urgency=0.5,
        context_signals={},
        history=history,
        class_priors=None,
    )
    # median of 10 and 30 is 20, then urgency 0.5 scales duration by 1.0
    assert exp.duration == 20.0
    assert exp.cost == 20.0
    assert exp.revenue == 20.0
    assert exp.duration != 999.0


def test_unknown_when_no_history_and_no_priors() -> None:
    exp = Expectation.compute(
        task_class="brand-new",
        urgency=0.5,
        context_signals={},
        history=[],
        class_priors=None,
    )
    assert exp.unknown is True
    assert exp.duration is None
    assert exp.cost is None
    assert exp.revenue is None
