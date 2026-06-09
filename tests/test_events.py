from datetime import date

from insuretra_pipeline.events import competitor_bleeding_from_snapshots, dump_guard_breached, tenure_months
from insuretra_pipeline.hashing import structural_hash


def link(agent_npn: str, agency_id: str, started: date, association_type: str = "Sub-Agent"):
    return {
        "agent_npn": agent_npn,
        "agency_tdi_id": agency_id,
        "association_type": association_type,
        "relationship_started_at": started,
        "first_seen_date": started,
        "confidence": "high",
        "structural_hash": structural_hash(agent_npn, agency_id, association_type),
    }


def test_tenure_months_handles_boundary():
    assert tenure_months(date(2024, 1, 1), date(2026, 1, 1)) == 24
    assert tenure_months(date(2024, 1, 2), date(2026, 1, 1)) == 23


def test_23_month_severance_is_suppressed():
    master = [link("9001", "npn:agency", date(2024, 1, 2))]
    events, suppressed = competitor_bleeding_from_snapshots(master, [], date(2026, 1, 1))

    assert events == []
    assert len(suppressed) == 1
    assert suppressed[0].suppression_reason == "TENURE_UNDER_24_MONTHS"
    assert suppressed[0].tenure_months == 23


def test_24_month_severance_creates_competitor_bleeding_event():
    master = [link("9001", "npn:agency", date(2024, 1, 1))]
    events, suppressed = competitor_bleeding_from_snapshots(master, [], date(2026, 1, 1))

    assert suppressed == []
    assert len(events) == 1
    assert events[0].event_type == "COMPETITOR_BLEEDING"
    assert events[0].target_agent_npn == "9001"


def test_non_sub_agent_severance_is_ignored():
    master = [link("9001", "npn:agency", date(2020, 1, 1), "Owner")]
    events, suppressed = competitor_bleeding_from_snapshots(master, [], date(2026, 1, 1))

    assert events == []
    assert suppressed == []


def test_duplicate_rerun_has_stable_event_fingerprint():
    master = [link("9001", "npn:agency", date(2024, 1, 1))]
    first, _ = competitor_bleeding_from_snapshots(master, [], date(2026, 1, 1))
    second, _ = competitor_bleeding_from_snapshots(master, [], date(2026, 1, 1))

    assert first[0].event_fingerprint == second[0].event_fingerprint


def test_dump_guard_threshold_behavior():
    breached, delta = dump_guard_breached({"links": 2000}, {"links": 100}, threshold=1500)
    assert breached is True
    assert delta == 1900

    breached, delta = dump_guard_breached({"links": 2000}, {"links": 0}, threshold=1500)
    assert breached is False
    assert delta == 2000

