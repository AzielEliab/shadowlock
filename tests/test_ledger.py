"""Ledger fields present: money_made, money_lost, money_left_on_table, net_variance, efficiency_score."""

from __future__ import annotations

from shadowlock.adapters import MemoryAdapter
from shadowlock.ledger import FinancialLedger
from shadowlock.session import ShadowLockSession

REQUIRED = (
    "money_made",
    "money_lost",
    "money_left_on_table",
    "net_variance",
    "efficiency_score",
)


def test_ledger_fields_present(jobs: list[dict], salt: str) -> None:
    report = ShadowLockSession(salt=salt).observe(MemoryAdapter(jobs))
    d = report.ledger.to_dict()
    for key in REQUIRED:
        assert key in d
        assert isinstance(d[key], (int, float))
    assert 0.0 <= d["efficiency_score"] <= 1.0
    assert "ledger" in report.to_dict()
    for key in REQUIRED:
        assert key in report.to_dict()["ledger"]


def test_ledger_arithmetic() -> None:
    from shadowlock.counterfactual import Expectation
    from shadowlock.envelope import JobEnvelope

    exp = Expectation(
        duration=50.0,
        duration_low=40.0,
        duration_high=60.0,
        cost=100.0,
        cost_low=80.0,
        cost_high=120.0,
        revenue=200.0,
        revenue_low=150.0,
        revenue_high=250.0,
    )
    # beat revenue, beat cost
    env = JobEnvelope(
        hashed_id="abc123def456",
        timestamp="2026-07-01T00:00:00Z",
        task_class="install",
        urgency=0.5,
        actual_revenue=230.0,
        actual_cost=90.0,
        actual_duration=40.0,
    )
    led = FinancialLedger()
    led.add(env, exp)
    assert led.money_made == 30.0
    assert led.money_lost == 0.0
    assert led.money_left_on_table == 0.0
    assert led.net_variance == 30.0
    assert 0.0 < led.efficiency_score <= 1.0

    # miss revenue, overrun cost
    env2 = JobEnvelope(
        hashed_id="abc123def457",
        timestamp="2026-07-01T00:00:00Z",
        task_class="install",
        urgency=0.5,
        actual_revenue=100.0,
        actual_cost=150.0,
        actual_duration=80.0,
    )
    led2 = FinancialLedger()
    led2.add(env2, exp)
    assert led2.money_made == 0.0
    assert led2.money_lost == (200.0 - 100.0) + (150.0 - 100.0)
    assert led2.money_left_on_table == 250.0 - 100.0
    assert led2.net_variance == led2.money_made - led2.money_lost
