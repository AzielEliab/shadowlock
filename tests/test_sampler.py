"""Sampler is deterministic; rate ~20% on 500 ids."""

from __future__ import annotations

from shadowlock.sample import SAMPLE_MODULUS, Sampler, identity_digest


def test_sampler_deterministic_same_salt_id() -> None:
    s = Sampler("alpha")
    assert s.should_sample("job-1") == s.should_sample("job-1")
    assert s.hashed_id("job-1") == s.hashed_id("job-1")
    # different salt may differ; different id may differ
    other = Sampler("beta")
    # formula is the documented construction
    digest = identity_digest("alpha", "job-1")
    expected = int.from_bytes(digest[:8], "big") % SAMPLE_MODULUS == 0
    assert s.should_sample("job-1") is expected


def test_sampler_rate_approx_20_percent_on_500_ids() -> None:
    s = Sampler("rate-salt")
    ids = [f"id-{i}" for i in range(500)]
    n = sum(1 for i in ids if s.should_sample(i))
    # Hash distribution: band around 20% (100), not a single number.
    assert 80 <= n <= 120, n
