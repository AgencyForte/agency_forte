# Insuretra

Insuretra is a pipeline-first V1 foundation for Texas insurance agency intelligence.

## What Is Included

- Next.js App Router admin shell.
- Supabase/Postgres/PostGIS migration.
- Python 3.11 pipeline package for TDI Socrata ingestion.
- Diff/event logic for Competitor Bleeding, Carrier Land-Grab, New Market Entry, and beta Trapped Talent candidates.
- 24-month Competitor Bleeding tenure filter with suppressed severance logging.
- GitHub Actions workflow for tests and scheduled/manual pipeline runs.

## What Is Not Included In V1

- Stripe or paid checkout.
- Public SEO pages.
- Sitemaps, canonical routes, or public agency profile pages.

## Environment

Copy `.env.example` and set:

- `NEXT_PUBLIC_SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `INSURETRA_ADMIN_PASSWORD`
- `DATABASE_URL`
- `SOCRATA_APP_TOKEN`
- `DUMP_GUARD_THRESHOLD`
- `OPS_WEBHOOK_URL`

## Commands

```bash
npm run dev
npm run build
python -m insuretra_pipeline.ingest --dataset all
python -m insuretra_pipeline.diff --dry-run
python -m insuretra_pipeline.run_daily
python -m insuretra_pipeline.seed_fixtures
pytest
```

