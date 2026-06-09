# Project Plan: Texas Agency Intelligence Engine

## 1. Delivery Strategy

The project will be delivered as a staged MVP build focused on proving the full intelligence loop:

1. Ingest official TDI data.
2. Detect structural market events.
3. Map events to local geographies.
4. Route events to subscribed users.
5. Sell high-value CSV export packs.

The plan assumes a 14-week MVP timeline with overlapping product, data, application, and QA workstreams. Timeline can compress or expand depending on team size, availability of production accounts, and how much historical TDI data is available for validation.

## 2. Recommended Team

Minimum delivery team:

- Technical lead / architect.
- Data engineer.
- Full-stack engineer.
- Product designer or design-capable frontend engineer.
- QA engineer, part-time.
- DevOps support, part-time.

Client-side support:

- Product owner.
- Business Development representative for pricing and packaging sign-off.
- Compliance/legal reviewer.
- Domain expert for insurance agency workflows.

## 3. Workstreams

### Product and UX

- MVP workflow definition.
- Dashboard and profile page UX.
- Paywall and checkout flows.
- Alert content patterns.
- Admin review flows.

### Data Engineering

- TDI endpoint validation.
- Schema mapping.
- Pipeline implementation.
- Hashing and diff logic.
- Dump guard and anomaly handling.
- Geospatial enrichment.

### Application Engineering

- Auth.
- Subscriptions.
- Dashboard.
- Profile pages.
- Event detail views.
- Export checkout and delivery.
- Admin tooling.

### QA, Security, and Launch

- Automated tests.
- Manual end-to-end validation.
- Data-quality review.
- Production readiness.
- Monitoring and incident response.

## 4. Milestone Timeline

| Phase | Duration | Primary Outcome |
| --- | --- | --- |
| 0. Kickoff and Technical Discovery | Week 1 | Validated requirements, accounts, endpoint inventory, architecture |
| 1. Data Foundation | Weeks 2-3 | Database schema, staging/master tables, geography tables |
| 2. Pipeline MVP | Weeks 4-5 | Nightly ingestion, hashing, diffing, dump guard |
| 3. Intelligence and Geo Routing | Weeks 6-7 | Four event types, ZIP/county matching, alert payloads |
| 4. SaaS Application Core | Weeks 6-9 | Auth, dashboard, watch areas, event views |
| 5. Monetization | Weeks 9-10 | Stripe subscriptions, paywall, CSV exports |
| 6. SaaS Hardening and V1 Distribution | Weeks 10-11 | Internal profile polish, entitlement hardening, alert/export refinement |
| 7. QA, Hardening, and Beta | Weeks 12-13 | Tests, staging dry runs, beta readiness |
| 8. Launch | Week 14 | Production deployment, monitoring, handoff |

## 5. Phase Details

### Phase 0: Kickoff and Technical Discovery

Duration: Week 1

Objectives:

- Confirm MVP interpretation from founding thesis and pipeline specification.
- Validate TDI source endpoints and field mappings.
- Confirm required accounts and environments.
- Finalize architecture and repository structure.
- Decide initial pricing placeholders and plan boundaries for implementation.

Key tasks:

- Create source-data inventory.
- Confirm Socrata resource IDs and API token requirements.
- Define normalized data contract for agencies, agents, carriers, appointments, and links.
- Confirm ZIP/county geography source.
- Establish dev, staging, and production environments.
- Create deployment and secrets inventory.

Deliverables:

- Technical architecture brief.
- Data mapping document.
- Environment checklist.
- Initial backlog.

Exit criteria:

- Engineering can ingest sample source data.
- Required services are provisioned or scheduled.
- No unresolved blocker prevents schema implementation.

### Phase 1: Data Foundation

Duration: Weeks 2-3

Objectives:

- Build the database foundation for the intelligence engine.
- Establish repeatable migrations.
- Prepare geospatial support.

Key tasks:

- Create Postgres(localized) project.
- Enable PostGIS.
- Implement master tables.
- Implement staging tables.
- Implement immutable market timeline.
- Implement relationship tenure metadata and suppressed severance logs.
- Implement pipeline logs and anomaly tables.
- Load Texas ZIP/county geometry or centroid data.
- Define indexes for identifiers, hashes, event dates, ZIPs, counties, and geography lookups.

Deliverables:

- Database migrations.
- Local/staging schema.
- Geography seed process.
- Initial database documentation.

Exit criteria:

- Schema can be recreated from migrations.
- Geometry data supports ZIP/county lookup.
- Core tables have appropriate constraints and indexes.

### Phase 2: Pipeline MVP

Duration: Weeks 4-5

Objectives:

- Build the scheduled ingestion and diffing pipeline.
- Protect against administrative data dumps.

Key tasks:

- Implement Python/Polars extract scripts.
- Normalize source fields.
- Compute structural hashes.
- Preserve relationship first-seen and effective-date data required for tenure calculation.
- Load staging tables using PostgreSQL COPY.
- Implement pre-diff validation.
- Implement configurable dump guard threshold.
- Implement SQL set operations for relationship differences.
- Implement master state UPSERT transaction.
- Write pipeline logs.
- Configure Slack or Discord operational alerts.
- Configure GitHub Actions cron schedule.

Deliverables:

- Nightly pipeline workflow.
- Data normalization module.
- Diff and consolidation scripts.
- Operational alert integration.
- Pipeline test suite.

Exit criteria:

- Pipeline runs successfully in staging.
- Re-running the same snapshot produces no duplicate threat events.
- Simulated bulk updates trigger quarantine behavior.
- Pipeline logs are queryable.

### Phase 3: Intelligence and Geo Routing

Duration: Weeks 6-7

Objectives:

- Generate usable intelligence events and route them by geography.

Key tasks:

- Implement Competitor Bleeding event generation.
- Implement the 24-month tenure filter for Competitor Bleeding alerts.
- Silently log short-tenure severed relationships without routing user-facing alerts.
- Implement Carrier Land-Grab event generation.
- Implement New Market Entry event generation.
- Implement Market Access Arbitrage candidate generation.
- Add event deduplication rules.
- Join events to ZIP and county geography.
- Implement radius matching where coordinate data supports it.
- Group events by user watch areas.
- Generate alert payload JSON.
- Mark processed events.

Deliverables:

- Four MVP event generators.
- Geo-tagging process.
- Alert routing process.
- Event payload schema.
- Event QA fixtures.

Exit criteria:

- Each MVP event type can be generated from controlled test data.
- Events are associated with a ZIP and county where source data allows.
- Alert payloads include the required event context.
- Processed events are not resent unless intentionally replayed.

### Phase 4: SaaS Application Core

Duration: Weeks 6-9

Objectives:

- Build the authenticated product experience.

Key tasks:

- Set up web application project.
- Implement authentication.
- Build onboarding flow.
- Build geography selection and watch-area management.
- Build dashboard with event feed.
- Build agency profile detail view.
- Build event detail view.
- Build saved competitor/watchlist feature.
- Build user alert preferences.
- Build basic admin dashboard for pipeline and event health.

Deliverables:

- Authenticated MVP application.
- User onboarding.
- Subscriber dashboard.
- Agency and event views.
- Admin health view.

Exit criteria:

- User can register, sign in, select geography, and view relevant events.
- Admin can inspect pipeline runs and event volume.
- Application uses authorization checks for paid data.

### Phase 5: Monetization

Duration: Weeks 9-10

Objectives:

- Enable paid subscriptions and one-off export purchases.

Key tasks:

- Configure Stripe products for ZIP, county, and regional subscription tiers.
- Implement checkout.
- Implement webhook handling.
- Store subscription status.
- Gate paid views and detailed intelligence.
- Implement export product catalog.
- Generate CSV exports.
- Implement export purchase and delivery flow.
- Create export audit records.

Deliverables:

- Subscription checkout.
- Webhook integration.
- Paywall enforcement.
- CSV export purchase flow.

Exit criteria:

- User can complete checkout and gain access to paid geography.
- Subscription cancellation or failure changes access appropriately.
- User can purchase and download a CSV export.
- Unauthorized users cannot access paid details.

### Phase 6: SaaS Hardening and V1 Distribution

Duration: Weeks 10-11

Objectives:

- Finalize the V1 SaaS-only distribution path.
- Harden internal profile views, entitlement checks, alert routing, and export workflows.
- Confirm programmatic SEO is excluded from V1 implementation.

Key tasks:

- Polish authenticated agency profile and event views.
- Verify paid intelligence is only available to authorized users.
- Validate subscription geography matching.
- Validate export purchase and delivery edge cases.
- Confirm alerts exclude short-tenure Competitor Bleeding records.
- Remove SEO-specific implementation tasks from the V1 backlog.

Deliverables:

- Hardened authenticated SaaS experience.
- Verified entitlement and paywall behavior.
- Refined alert and export flows.
- V2 note for future programmatic SEO scope.

Exit criteria:

- Authenticated users can view internal agency and event intelligence appropriate to their subscription.
- Paid details remain gated.
- Short-tenure Competitor Bleeding records remain suppressed from user-facing surfaces.
- No V1 delivery task depends on public agency profile pages, sitemaps, canonical routes, or SEO metadata.

### Phase 7: QA, Hardening, and Beta

Duration: Weeks 12-13

Objectives:

- Validate product behavior, data quality, and launch readiness.

Key tasks:

- Run dry pipeline executions in staging.
- Validate event generation against controlled fixtures.
- Review sample events with domain expert.
- Test checkout and webhook behavior.
- Test alert delivery.
- Test export delivery.
- Perform permission and paywall testing.
- Add error handling for endpoint failures.
- Add backups and recovery process.
- Fix critical usability issues.

Deliverables:

- QA report.
- Beta readiness checklist.
- Known issues log.
- Production launch checklist.

Exit criteria:

- Critical user journeys pass end-to-end.
- Pipeline failures are visible to operations.
- False-positive risk is documented and mitigated.
- Product owner approves beta release.

### Phase 8: Launch

Duration: Week 14

Objectives:

- Deploy production MVP and hand off operations.

Key tasks:

- Deploy production database.
- Deploy production web application.
- Configure production secrets.
- Enable scheduled pipeline.
- Enable production monitoring.
- Verify Stripe live-mode configuration.
- Verify email domain configuration.
- Perform smoke tests.
- Document operational procedures.

Deliverables:

- Production MVP.
- Launch notes.
- Operations runbook.
- Handoff session.

Exit criteria:

- Production users can subscribe and access intelligence.
- Nightly pipeline runs in production.
- Alerts and exports function in production.
- Admin can monitor data and system health.

## 6. Backlog Structure

### Epic 1: Data Source Integration

- Validate TDI endpoints.
- Implement authenticated Socrata requests.
- Normalize records.
- Handle nulls and malformed rows.
- Store raw ingestion metadata.

### Epic 2: Master State and Diffing

- Create master tables.
- Create staging tables.
- Compute hashes.
- Implement set-based diffs.
- Implement UPSERT consolidation.
- Add idempotency protections.

### Epic 3: Threat Intelligence

- Generate Competitor Bleeding alerts.
- Enforce the 24-month tenure filter for Competitor Bleeding alerts.
- Log short-tenure severed relationships without user-facing alert generation.
- Generate Carrier Land-Grab alerts.
- Generate New Market Entry alerts.
- Generate Market Access Arbitrage candidates.
- Deduplicate events.
- Store timeline records.

### Epic 4: Geography and Routing

- Load Texas ZIP/county data.
- Normalize ZIP codes.
- Associate agencies to geography.
- Match events to watch areas.
- Generate alert payloads.

### Epic 5: SaaS Product

- Authentication.
- Onboarding.
- Dashboard.
- Agency profile views.
- Event detail views.
- Watch areas.
- Alert preferences.
- Admin health dashboard.

### Epic 6: Monetization

- Stripe products.
- Subscription checkout.
- Webhooks.
- Access control.
- CSV export products.
- Export audit trail.

### Epic 7: SaaS Hardening and V1 Distribution

- Internal agency profile polish.
- Entitlement verification.
- Alert routing refinement.
- Export delivery refinement.
- V2 programmatic SEO scope note.

### Epic 8: QA and Operations

- Unit tests.
- Integration tests.
- End-to-end tests.
- Pipeline monitoring.
- Alert monitoring.
- Backup and recovery.
- Launch checklist.

## 7. Testing Plan

### Data Tests

- Field mapping validation.
- ZIP normalization validation.
- Hash stability tests.
- Idempotent rerun tests.
- Simulated deletion/addition tests.
- Competitor Bleeding tenure filter tests for relationships under and over 24 months.
- Bulk-update quarantine tests.

### Application Tests

- Authentication flow.
- Subscription checkout.
- Paid access enforcement.
- Dashboard filtering.
- Export purchase and download.
- Admin pipeline visibility.

### End-to-End Tests

- Subscriber selects county watch area and sees relevant events.
- Pipeline detects a severed 23-month agent-agency relationship and logs it without alerting users.
- Pipeline detects a severed 24-month agent-agency relationship and routes a Competitor Bleeding alert.
- Pipeline generates a Carrier Land-Grab event and routes an email alert.
- User purchases trapped talent CSV export.
- Admin reviews a quarantined pipeline run.

## 8. Deployment Plan

Environments:

- Local development.
- Staging.
- Production.

Recommended deployment services:

- GitHub for source control and scheduled pipeline workflows.
- Supabase for Postgres/PostGIS.
- Vercel or comparable platform for web application hosting.
- Stripe for payments.
- Resend or comparable provider for email.
- Slack or Discord for operational alerts.

Deployment sequence:

1. Provision staging services.
2. Deploy database migrations.
3. Run sample ingestion.
4. Deploy web application.
5. Configure payment test mode.
6. Complete staging QA.
7. Provision production services.
8. Deploy production migrations.
9. Deploy production application.
10. Enable live payment mode.
11. Enable scheduled production pipeline.
12. Perform production smoke test.

## 9. Definition of Done

A feature is done when:

- It is implemented in the target environment.
- It has appropriate automated tests or documented manual validation.
- It handles expected error cases.
- It respects access-control requirements.
- It logs operationally relevant failures.
- It is documented sufficiently for handoff.
- It is reviewed and accepted by the product owner or technical lead.

## 10. Critical Dependencies

- Confirmed TDI Socrata resource IDs.
- Socrata application token.
- Supabase project with PostGIS enabled.
- Texas ZIP/county geometry source.
- Stripe account and product approval.
- Email provider account and sending domain.
- Hosting provider account.
- Slack or Discord webhook.
- Final legal review of SaaS paywall, alert, and data-use copy.
- Product owner availability for sample event review.

## 11. Launch Readiness Checklist

- Production database migrations applied.
- Production secrets configured.
- Pipeline cron enabled.
- Pipeline run verified.
- Dump guard tested.
- Operational alerts tested.
- Stripe live checkout tested.
- Stripe webhooks tested.
- Email delivery tested.
- Paid data hidden from anonymous users.
- CSV exports generate and download.
- Admin health dashboard accessible.
- Backup process configured.
- Legal/compliance copy approved.
- Product owner launch approval received.

## 12. Post-Launch Roadmap Candidates

After MVP launch, the highest-value enhancements are likely to be:

- Historical trend charts by agency and geography.
- V2 programmatic SEO, including public-facing agency profile pages, sitemaps, canonical routing, and indexable metadata.
- Carrier importance scoring.
- Producer movement confidence scores.
- CRM integrations.
- Automated direct-mail or ad campaign integrations.
- Multi-state expansion.
- Recruiter-specific workflows.
- Enterprise team accounts.
- Advanced M&A prospecting.
- AI-assisted playbook recommendations.
