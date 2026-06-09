from __future__ import annotations

import polars as pl


def normalize_zip(expr: pl.Expr) -> pl.Expr:
    return (
        expr.cast(pl.Utf8)
        .str.replace_all(r"\D", "")
        .str.slice(0, 5)
        .replace("", None)
    )


def normalize_text(expr: pl.Expr) -> pl.Expr:
    return (
        expr.cast(pl.Utf8)
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .replace("", None)
    )


def parse_date(expr: pl.Expr) -> pl.Expr:
    return pl.coalesce(
        expr.str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%S%.f", strict=False),
        expr.str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%S", strict=False),
        expr.str.strptime(pl.Date, "%Y-%m-%d", strict=False),
        expr.str.strptime(pl.Date, "%m/%d/%Y", strict=False),
    )


def agency_id_from_npn_or_license(npn_expr: pl.Expr, license_expr: pl.Expr) -> pl.Expr:
    npn_norm = normalize_text(npn_expr)
    lic_norm = normalize_text(license_expr)
    return (
        pl.when(npn_norm.is_not_null())
        .then(pl.lit("npn:") + npn_norm)
        .when(lic_norm.is_not_null())
        .then(pl.lit("lic:") + lic_norm)
        .otherwise(pl.lit(None))
    )


def structural_hash_expr(*exprs: pl.Expr) -> pl.Expr:
    return pl.concat_str([pl.lit("SHA256")] + [e.cast(pl.Utf8).fill_null("") for e in exprs], separator="|").hash().cast(pl.Utf8)


def normalize_agency(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        agency_id_from_npn_or_license(pl.col("NPN"), pl.col("License number")).alias("agency_tdi_id"),
        normalize_text(pl.col("NPN")).alias("agency_npn"),
        pl.lit(None).cast(pl.Utf8).alias("agency_ein"),
        normalize_text(pl.col("Name")).alias("name"),
        normalize_text(pl.col("Org type")).alias("agency_type"),
        normalize_text(pl.col("License type")).alias("license_type"),
        normalize_text(pl.col("Qualification")).alias("qualification"),
        parse_date(pl.col("Issue date")).alias("license_issue_date"),
        parse_date(pl.col("Expiration date")).alias("expiration_date"),
        normalize_text(pl.col("City")).alias("city"),
        normalize_text(pl.col("State")).alias("state"),
        normalize_zip(pl.col("Postal code")).alias("postal_code"),
        normalize_text(pl.col("County (if title agency)")).alias("county"),
    ])
    return df.select([
        "agency_tdi_id", "agency_npn", "agency_ein", "name", "agency_type",
        "license_type", "qualification", "license_issue_date", "expiration_date",
        "city", "state", "postal_code", "county"
    ]).drop_nulls(subset=["agency_tdi_id", "name"])


def normalize_relationship(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        normalize_text(pl.col("Associated licensee NPN")).alias("agent_npn"),
        normalize_text(pl.col("Associated licensee name")).alias("agent_name"),
        agency_id_from_npn_or_license(pl.col("Licensee NPN"), pl.lit(None)).alias("agency_tdi_id"),
        normalize_text(pl.col("Licensee EIN")).alias("agency_ein"),
        normalize_text(pl.col("Licensee name")).alias("agency_name"),
        normalize_text(pl.col("Association type")).alias("association_type"),
        parse_date(pl.col("Association begin date")).alias("relationship_started_at"),
    ])
    df = df.with_columns([
        pl.when(pl.col("relationship_started_at").is_not_null())
        .then(pl.lit("high"))
        .otherwise(pl.lit("lower_first_seen_fallback"))
        .alias("confidence"),
        structural_hash_expr(pl.col("agent_npn"), pl.col("agency_tdi_id"), pl.col("association_type")).alias("structural_hash"),
    ])
    return df.select([
        "agent_npn", "agent_name", "agency_tdi_id", "agency_ein", "agency_name",
        "association_type", "relationship_started_at", "confidence", "structural_hash"
    ]).drop_nulls(subset=["agent_npn", "agency_tdi_id", "association_type", "structural_hash"])


def normalize_agency_appointment(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        agency_id_from_npn_or_license(pl.col("Agency NPN"), pl.lit(None)).alias("agency_tdi_id"),
        normalize_text(pl.col("Agency EIN")).alias("agency_ein"),
        normalize_text(pl.col("Agency name")).alias("agency_name"),
        normalize_text(pl.col("NAIC ID")).alias("carrier_naic"),
        normalize_text(pl.col("Insurance company name")).alias("carrier_name"),
        normalize_text(pl.col("Appointment type")).alias("appointment_type"),
        parse_date(pl.col("Appointment active date")).alias("effective_date"),
        normalize_text(pl.col("City")).alias("city"),
        normalize_text(pl.col("State")).alias("state"),
        normalize_zip(pl.col("Postal code")).alias("postal_code"),
    ])
    df = df.with_columns([
        structural_hash_expr(pl.col("agency_tdi_id"), pl.col("carrier_naic"), pl.col("appointment_type")).alias("structural_hash"),
    ])
    return df.select([
        "agency_tdi_id", "agency_ein", "agency_name", "carrier_naic", "carrier_name",
        "appointment_type", "effective_date", "city", "state", "postal_code", "structural_hash"
    ]).drop_nulls(subset=["agency_tdi_id", "carrier_naic", "carrier_name", "structural_hash"])


def normalize_agent_appointment(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        normalize_text(pl.col("Agent NPN")).alias("agent_npn"),
        normalize_text(pl.col("Agent name")).alias("agent_name"),
        normalize_text(pl.col("NAIC ID")).alias("carrier_naic"),
        normalize_text(pl.col("Insurance company name")).alias("carrier_name"),
        normalize_text(pl.col("Appointment type")).alias("appointment_type"),
        parse_date(pl.col("Appointment active date")).alias("effective_date"),
        normalize_text(pl.col("City")).alias("city"),
        normalize_text(pl.col("State")).alias("state"),
        normalize_zip(pl.col("Postal code")).alias("postal_code"),
    ])
    df = df.with_columns([
        structural_hash_expr(pl.col("agent_npn"), pl.col("carrier_naic"), pl.col("appointment_type")).alias("structural_hash"),
    ])
    return df.select([
        "agent_npn", "agent_name", "carrier_naic", "carrier_name", "appointment_type",
        "effective_date", "city", "state", "postal_code", "structural_hash"
    ]).drop_nulls(subset=["agent_npn", "carrier_naic", "carrier_name", "structural_hash"])


NORMALIZERS = {
    "agencies": normalize_agency,
    "relationships": normalize_relationship,
    "agency_appointments": normalize_agency_appointment,
    "agent_appointments": normalize_agent_appointment,
}


def normalize_rows(dataset_key: str, df: pl.DataFrame) -> pl.DataFrame:
    if df.is_empty():
        # Handle empty dataframes by running the normalizer on it anyway to get correct schema
        return NORMALIZERS[dataset_key](df)
    return NORMALIZERS[dataset_key](df)

