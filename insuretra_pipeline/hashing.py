from __future__ import annotations

import hashlib


def normalize_hash_part(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def structural_hash(*parts: object) -> str:
    payload = "|".join(normalize_hash_part(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

