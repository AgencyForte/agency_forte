from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .hashing import structural_hash


@dataclass(frozen=True)
class GeneratedEvent:
    event_type: str
    event_fingerprint: str
    target_agency_id: str | None = None
    target_agent_npn: str | None = None
    carrier_naic: str | None = None
    carrier_name: str | None = None
    event_zip: str | None = None
    confidence: str = "high"
    payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class SuppressedSeverance:
    agent_npn: str
    agency_tdi_id: str
    association_type: str
    relationship_started_at: date | None
    relationship_ended_at: date
    tenure_months: int | None
    suppression_reason: str
    structural_hash: str
    payload: dict[str, Any]


def tenure_months(start: date | None, end: date) -> int | None:
    if start is None or start > end:
        return None
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def competitor_bleeding_from_snapshots(
    master_links: list[dict[str, Any]],
    stage_links: list[dict[str, Any]],
    detected_on: date,
    minimum_months: int = 24,
) -> tuple[list[GeneratedEvent], list[SuppressedSeverance]]:
    stage_hashes = {link["structural_hash"] for link in stage_links}
    events: list[GeneratedEvent] = []
    suppressed: list[SuppressedSeverance] = []

    for link in master_links:
        if link.get("structural_hash") in stage_hashes:
            continue
        if str(link.get("association_type", "")).strip().lower() != "sub-agent":
            continue

        started_at = link.get("relationship_started_at") or link.get("first_seen_date")
        months = tenure_months(started_at, detected_on)
        payload = {
            "association_type": link.get("association_type"),
            "tenure_months": months,
            "source_rule": "24_month_tenure_filter",
        }

        if months is not None and months >= minimum_months:
            fingerprint = structural_hash("COMPETITOR_BLEEDING", link.get("agent_npn"), link.get("agency_tdi_id"), detected_on)
            events.append(
                GeneratedEvent(
                    event_type="COMPETITOR_BLEEDING",
                    event_fingerprint=fingerprint,
                    target_agency_id=link.get("agency_tdi_id"),
                    target_agent_npn=link.get("agent_npn"),
                    confidence=link.get("confidence", "high"),
                    payload=payload,
                )
            )
        else:
            suppressed.append(
                SuppressedSeverance(
                    agent_npn=link["agent_npn"],
                    agency_tdi_id=link["agency_tdi_id"],
                    association_type=link["association_type"],
                    relationship_started_at=started_at,
                    relationship_ended_at=detected_on,
                    tenure_months=months,
                    suppression_reason="TENURE_UNDER_24_MONTHS",
                    structural_hash=link["structural_hash"],
                    payload=payload,
                )
            )

    return events, suppressed


def dump_guard_breached(stage_counts: dict[str, int], master_counts: dict[str, int], threshold: int) -> tuple[bool, int]:
    master_total = sum(master_counts.values())
    if master_total == 0:
        return False, sum(stage_counts.values())
    delta = sum(abs(stage_counts.get(key, 0) - master_counts.get(key, 0)) for key in set(stage_counts) | set(master_counts))
    return delta > threshold, delta

