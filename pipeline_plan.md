# Insuretra Pipeline-First Implementation Plan

## Summary

Build the first implementation pass as a pipeline-first V1 foundation for **Insuretra**, using **Next.js + Supabase/Postgres/PostGIS**, with **no payments yet**. The deliverable is a working data platform foundation: database schema, TDI ingestion scripts, diff/event generation, 24-month Competitor Bleeding filter, dump guard, suppressed severance logging, pipeline tests, and a minimal authenticated admin/dashboard shell to inspect pipeline outputs.

Primary source datasets are the TDI public open-data resources listed by TDI as company appointments and business relationships for agents/agencies, including:
- Agency appointments: `avjc-7u2m`
- Agent appointments: `ft7p-v8a7`
- Agent/agency/business relationships: `kvqi-vsrr`
- Agency license master data: `3yqc-fcdt`

Sources: [TDI list page](https://tdi.texas.gov/agent/agentlists.html), [agent appointments dataset](https://data.texas.gov/dataset/Active-insurance-company-appointments-for-agents-a/ft7p-v8a7), [agency appointment catalog metadata](https://catalog.data.gov/dataset/active-insurance-company-appointments-for-agencies-and-businesses).

## Key Implementation Changes

- Scaffold Insuretra with Next.js App Router, TypeScript, Tailwind, Supabase client/server helpers, and a minimal admin UI.
- Add Supabase SQL migrations for:
  - `master_agencies`, `master_agents`, `master_agent_agency_links`, `master_agency_appointments`, `master_agent_appointments`
  - `market_timeline`
  - `suppressed_severances`
  - `pipeline_runs`, `pipeline_logs`, `pipeline_anomalies`
  - staging tables for all ingested datasets
  - PostGIS-enabled ZIP/county geometry placeholders
- Add Python 3.11 pipeline package using Polars and psycopg:
  - fetch Socrata CSV/JSON using `SOCRATA_APP_TOKEN`
  - normalize TDI fields
  - load staging tables
  - compute structural hashes
  - run dump guard using default threshold `1500`
  - generate events
  - consolidate master state
- Implement event logic:
  - `COMPETITOR_BLEEDING`: severed `Sub-Agent` relationships only, with 24-month continuous tenure required
  - under-24-month severances go to `suppressed_severances`, never `market_timeline`
  - `CARRIER_LAND_GRAB`: new agency-carrier appointment for agencies older than 30 days
  - `NEW_MARKET_ENTRY`: new agency record from `3yqc-fcdt`
  - `TRAPPED_TALENT_IDENTIFIED`: create candidate generation stub using agent appointments plus agency carrier access; mark as beta/manual-review quality
- Add minimal Insuretra admin/dashboard:
  - pipeline run list
  - anomaly list
  - market timeline table
  - suppressed severance table
  - event detail view
  - no Stripe, no checkout, no public SEO pages
- Add GitHub Actions workflow:
  - nightly pipeline job
  - manual dispatch support
  - env vars: `DATABASE_URL`, `SOCRATA_APP_TOKEN`, `DUMP_GUARD_THRESHOLD`, optional `OPS_WEBHOOK_URL`

## Public Interfaces / Commands

- CLI commands:
  - `python -m insuretra_pipeline.ingest --dataset all`
  - `python -m insuretra_pipeline.run_daily`
  - `python -m insuretra_pipeline.diff --dry-run`
  - `python -m insuretra_pipeline.seed_fixtures`
- Next.js routes:
  - `/` branded Insuretra landing/dashboard redirect
  - `/admin/pipeline-runs`
  - `/admin/events`
  - `/admin/suppressed-severances`
  - `/admin/anomalies`
- Event statuses:
  - `pending_review`
  - `approved`
  - `rejected`
  - `suppressed_by_rule`
  - `quarantined`
- Event types:
  - `NEW_MARKET_ENTRY`
  - `CARRIER_LAND_GRAB`
  - `COMPETITOR_BLEEDING`
  - `TRAPPED_TALENT_IDENTIFIED`

## Test Plan

- Unit tests:
  - Socrata field normalization for all four datasets
  - structural hash stability
  - ZIP normalization
  - dump guard threshold behavior
  - 23-month severance is suppressed
  - 24-month severance creates `COMPETITOR_BLEEDING`
  - duplicate pipeline rerun does not duplicate events
- Integration tests:
  - fixture ingestion into staging
  - staging-to-master consolidation
  - event generation from controlled before/after snapshots
  - suppressed severances hidden from timeline output
- UI smoke tests:
  - admin can view pipeline runs
  - admin can view market events
  - admin can view suppressed severances
  - no public SEO/profile routes exist
- Acceptance scenarios:
  - Pipeline ingests sample TDI records and produces normalized staging rows
  - Dump guard quarantines a simulated large statewide delta
  - Valid carrier appointment addition creates a `CARRIER_LAND_GRAB`
  - New agency creates a `NEW_MARKET_ENTRY`
  - Short-tenure severed relationship is logged only
  - 24-month severed relationship creates a user-facing timeline event

## Assumptions And Defaults

- First pass is **Pipeline First**, not full customer SaaS.
- Stack is **Next.js + Supabase/Postgres/PostGIS**.
- Payments are excluded for now; no Stripe implementation.
- App name and brand label is **Insuretra**.
- Programmatic SEO remains V2-only and must not be implemented.
- Use TDI Socrata resource IDs `avjc-7u2m`, `ft7p-v8a7`, `kvqi-vsrr`, and `3yqc-fcdt`.
- Use `association_type = "Sub-Agent"` as the V1 signal for agent-agency producer relationship severance.
- Use `association_begin_date` when present for tenure; otherwise fall back to first-seen date and mark confidence lower.
- Use a default dump guard threshold of `1500`, configurable by env var.
- Use local fixture data for tests so CI does not depend on live TDI availability.
