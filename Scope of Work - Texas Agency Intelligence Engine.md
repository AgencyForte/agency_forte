# Scope of Work: Texas Agency Intelligence Engine

## 1. Executive Summary

The Texas Agency Intelligence Engine is a self-serve SaaS platform that transforms public Texas Department of Insurance (TDI) relationship and appointment data into actionable competitive intelligence for independent insurance agency owners in Texas.

The MVP will ingest agency, agent, carrier appointment, and agent-agency relationship data from official TDI open-data endpoints; detect meaningful structural changes; map those changes to ZIP/county geographies; and deliver offensive market intelligence alerts, authenticated SaaS profile views, and paid exports to subscribing users.

No Business Development blocker is identified from the provided materials. This scope proceeds on the assumption that the MVP will target mid-market independent agency owners and principals in Texas, with monetization through geographic subscriptions and pay-per-pack data exports.

## 2. Business Objectives

The project will deliver a product that enables Texas independent agency owners to:

1. Detect competitor weakness when rival agencies lose producers.
2. Identify recruitable licensed producers who may be trapped at under-resourced agencies.
3. Anticipate competitor market moves when rivals add valuable specialty carriers.
4. Discover new agency or branch registrations in their target ZIP codes.
5. Search, monitor, and compare local agency profiles.
6. Purchase focused data exports for recruiting, market expansion, or competitive analysis.

## 3. Target Users

Primary users are Texas-based independent insurance agency owners, principals, and operators who:

- Compete in localized geographic markets.
- Depend on producer relationships and carrier access.
- Lack dedicated recruiting, M&A, or market intelligence teams.
- Need practical intelligence within a 10 to 25 mile operating radius.
- Are willing to pay for localized alerts, competitor monitoring, and talent intelligence.

Secondary users may include:

- Agency growth consultants.
- Insurance recruiters.
- Roll-up groups and acquisition teams.
- Carrier field representatives.

Secondary users are not the primary MVP design target unless explicitly prioritized later.

## 4. MVP Scope

### 4.1 Data Ingestion

The system will ingest the following nightly from official TDI open-data endpoints:

- Agency-carrier appointment relationships.
- Agent-carrier appointment relationships.
- Agent-agency/business relationships.

The ingestion pipeline will:

- Run on a scheduled GitHub Actions workflow.
- Use Python 3.11 and Polars for bulk data processing.
- Pull from sanctioned Socrata `/resource` API endpoints.
- Use an application token for stable rate limits.
- Avoid scraping the TDI website or UI.
- Normalize nulls, identifiers, dates, agency names, carrier names, and ZIP codes.
- Compute cryptographic structural hashes for relationship records.
- Load data into ephemeral staging tables before production consolidation.

### 4.2 Database and Storage

The MVP will use PostgreSQL with Supabase and PostGIS.

Core schema areas will include:

- Master agency state.
- Master agent state.
- Master agent-agency links.
- Master agency-carrier appointments.
- Master agent-carrier appointments where needed for trapped talent analysis.
- Relationship first-seen, effective-date, and severance metadata needed to calculate 24-month continuous tenure.
- Immutable market timeline events.
- Suppressed severance logs for short-tenure Competitor Bleeding candidates.
- Static Texas ZIP/county geography tables.
- Pipeline logs and anomaly records.
- User accounts, subscriptions, watch areas, saved agencies, and alert preferences.
- Export orders and generated export files or file references.

### 4.3 Administrative Dump Guard

The system will include a data-quality guard to prevent false-positive alerts caused by statewide administrative updates or carrier migration events.

The guard will:

- Compare staging and production row counts during each run.
- Detect unusual statewide deltas above a configured threshold.
- Suppress event generation during suspected bulk administrative updates.
- Update master state safely using structural hashes.
- Log quarantine events.
- Notify the operations channel through Slack or Discord webhook.

The initial threshold described in the source material is 1,500 statewide changed rows in a 24-hour cycle. The final production threshold will be configurable by environment variable.

### 4.4 Threat Event Generation

The MVP will generate four intelligence event types.

#### Competitor Bleeding Alert

Detects agents or producers previously linked to an agency who are no longer present in the latest TDI relationship data.

The 24-Month Tenure Filter:

- The pipeline must calculate the duration of the severed agent-agency relationship.
- A user-facing `COMPETITOR_BLEEDING` event will only be generated if the agent was continuously associated with the agency for at least 24 months.
- Severed relationships lasting less than 24 months will be silently logged and excluded from alerts, dashboards, and paid exports intended to represent competitor bleeding.
- The purpose of this filter is to suppress low-value noise from rookie turnover, short trial periods, administrative corrections, or brief producer affiliations.

User value:

- Indicates possible orphaned accounts.
- Supports targeted marketing in the affected ZIP/county.
- Supports recruiting or competitive outreach.

MVP output:

- A timeline event tied to the affected agency, agent NPN, ZIP, and detection date.
- Alert payload for subscribed users monitoring the affected geography.

#### Market Access Arbitrage

Identifies producers who appear active and valuable but are associated with agencies with weaker or narrower carrier access than a subscribing buyer.

User value:

- Supports producer recruiting.
- Frames recruiting around superior market access rather than compensation alone.

MVP output:

- Trapped talent candidate records.
- Exportable county-level or region-level rosters.
- Paywalled detail including names, NPNs, carrier context, and relationship history.

#### Carrier Land-Grab Radar

Detects when an existing local agency adds a new carrier appointment, especially major specialty or high-value carriers.

User value:

- Gives subscribers a leading indicator that a competitor may begin targeting new account segments.
- Supports defensive account retention campaigns.

MVP output:

- A timeline event tied to agency, carrier, ZIP, and detection date.
- Alerts to users monitoring affected geographies.

#### New Market Entry

Detects newly registered agency entities or physical branch offices in target geographies.

User value:

- Alerts incumbent agencies to new local competition.
- Supports retention, local marketing, and competitor tracking.

MVP output:

- A timeline event tied to agency ID, ZIP, and detection date.
- Alert payload to affected subscribers.

### 4.5 Geospatial Intelligence

The platform will map events to Texas geographies.

MVP geospatial functionality will include:

- ZIP-level association for agencies and events.
- County-level grouping.
- Radius-based matching using PostGIS where reliable latitude/longitude or ZIP centroid data is available.
- Subscription watch areas by ZIP, county, and region.
- Event routing to users whose watch areas overlap the event geography.

### 4.6 SaaS Web Application

The MVP web application will include:

- User authentication.
- Account onboarding.
- Selection of monitored geography.
- Subscription checkout and plan management.
- Dashboard showing local threat events.
- Agency profile pages.
- Saved competitors or watched agencies.
- Alert preferences.
- Export purchase flow.
- Basic admin view for pipeline health, users, and event review.

Recommended implementation stack:

- Next.js or equivalent modern React framework.
- Supabase for database, auth integration support, and Postgres.
- Stripe for subscriptions and one-off export purchases.
- Resend or comparable provider for transactional and alert email.
- Vercel or comparable platform for web hosting.

The exact web framework can be adjusted during technical kickoff if an existing codebase or company standard already exists.

### 4.7 V1 Distribution Scope

Programmatic SEO is officially descoped from the V1 MVP.

V1 distribution will be limited to the authenticated SaaS application and any manually operated sales, onboarding, or customer success motion outside the software scope. The V1 product will not include public-facing agency profile pages, sitemap generation, canonical routing, indexable profile templates, or SEO-specific metadata workflows.

Programmatic SEO profile pages may be reconsidered as a V2 roadmap item after the SaaS intelligence loop, subscription model, data quality controls, and paid export workflows are validated.

### 4.8 Alerts and Notifications

The MVP will support email alerts for subscribed users.

Alert payloads will include:

- Event type.
- Affected agency.
- Event geography.
- Detection date.
- Plain-English summary.
- Link to the relevant profile or event detail page.

Operational alerts will include:

- Pipeline success or failure.
- Bulk update quarantine.
- Endpoint failures.
- Unexpected schema changes.
- Abnormal event volume.

### 4.9 Paid Exports

The MVP will support pay-per-pack exports.

Initial export types:

- Trapped talent roster by county.
- Competitor changes by county or ZIP.
- Agency-carrier appointment changes by geography.

Export format:

- CSV for MVP.
- Optional JSON export for internal/admin use.

Each export will include:

- Purchase record.
- User association.
- Generated timestamp.
- Geography.
- Data provenance identifiers such as agency TDI ID and agent NPN.

### 4.10 Compliance and Data Provenance

The system will:

- Use official public-data endpoints.
- Avoid scraping restricted or unofficial UI surfaces.
- Store raw public identifiers necessary for auditability.
- Display appropriate source and freshness disclaimers.
- Track data detection dates separately from source effective dates.
- Maintain pipeline logs for troubleshooting and data challenges.

Legal review of marketing copy, privacy posture, and data-use disclaimers is recommended before public launch.

## 5. Out of Scope for MVP

The following are not included in the MVP unless added through change control:

- Expansion beyond Texas.
- Real-time alerts faster than the TDI reporting/update cadence.
- Guaranteed producer employment status verification outside public records.
- CRM integrations.
- Automated ad buying or direct-mail campaign execution.
- AI-generated sales scripts or recruiting outreach automation.
- Programmatic SEO, including public agency profile pages, sitemaps, canonical routing, and indexable profile metadata.
- Native mobile applications.
- Enterprise custom pricing workflow.
- Complex role-based enterprise account hierarchies.
- Manual research services performed by analysts.
- Full M&A prospecting module.
- Carrier-specific private-data integrations.

## 6. Deliverables

### 6.1 Architecture and Planning

- Finalized technical architecture.
- Data source inventory and endpoint validation.
- Database schema migration files.
- Environment and deployment plan.
- Monitoring and incident response plan.

### 6.2 Data Pipeline

- Scheduled extraction workflow.
- Staging table load process.
- Structural hash generation.
- Administrative dump guard.
- Diff-based event generation.
- Agent-agency tenure calculation for Competitor Bleeding filtering.
- Suppressed severance logging for relationships under 24 months.
- Master state consolidation.
- Pipeline logging.
- Slack or Discord operational notifications.

### 6.3 Intelligence Engine

- Threat event generation for all four MVP event categories.
- Geospatial event tagging.
- Watch-area matching.
- Event deduplication and processing status management.
- Export dataset generation.

### 6.4 Web Application

- Authenticated user experience.
- Subscription onboarding.
- Dashboard.
- Agency profile pages.
- Event detail pages.
- Watch geography management.
- Export purchase and download flow.
- Admin health dashboard.

### 6.5 V1 SaaS Distribution

- Authenticated SaaS access model.
- Internal agency profile and event views for authorized users.
- Paywall enforcement for subscription and export entitlements.
- No public agency profile generation, sitemap generation, canonical routing, or SEO metadata deliverables in V1.

### 6.6 QA and Launch

- Automated unit and integration tests for pipeline logic.
- Database migration validation.
- End-to-end tests for primary user flows.
- Backfill/dry-run validation against historical or repeated TDI snapshots where available.
- Production deployment.
- Launch checklist and handoff documentation.

## 7. Acceptance Criteria

The MVP will be considered accepted when:

1. The pipeline successfully ingests the three target TDI datasets from official endpoints.
2. Staging, master, and timeline tables are populated through repeatable migrations and scheduled runs.
3. Structural hashes prevent artificial relationship churn from producing duplicate events.
4. The administrative dump guard suppresses event generation when configured anomaly thresholds are exceeded.
5. Competitor Bleeding events are only user-facing when the severed agent-agency relationship lasted at least 24 continuous months.
6. Short-tenure severed relationships are logged without generating user-facing alerts.
7. Each of the four MVP event types can be generated, stored, viewed, and routed.
8. Events can be associated with ZIP/county geography.
9. A user can create an account, select a monitored geography, subscribe, and view relevant local intelligence.
10. Paid details are visible only to authorized users.
11. A user can purchase and download at least one CSV export type.
12. Email alerts are sent for qualifying events.
13. Admin users can inspect pipeline runs, anomalies, short-tenure suppressed severances, and recent event volume.
14. Core flows pass automated and manual QA in staging.
15. Production deployment is complete with required secrets, monitoring, and backup configuration.

## 8. Assumptions

- TDI datasets are available through Socrata-compatible public endpoints.
- The client will provide or approve accounts for Supabase, GitHub, Stripe, email delivery, hosting, and Slack/Discord.
- The MVP will launch in Texas only.
- Geographic monitoring tiers will be ZIP, county, and regional.
- Initial carrier importance ranking can be configured manually and improved later.
- Programmatic SEO is a V2 candidate and is not part of the V1 MVP.
- Final pricing, plan names, and trial length can be inserted during implementation without blocking architecture.
- Exact endpoint resource IDs and field mappings will be confirmed during technical discovery.
- Legal/compliance review will be provided by the client before public launch.

## 9. Key Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| TDI endpoint schema changes | Pipeline failure or incorrect data mapping | Schema validation, pipeline logs, operational alerts |
| Public data lag | Users may expect real-time intelligence | Product copy will frame alerts as strategic market intelligence, not real-time alarms |
| Administrative data dumps | False positives | Configurable dump guard and structural hashing |
| Weak ZIP/address data | Poor event routing | ZIP normalization, county fallback, static geography tables |
| Data sensitivity perception | Reputational or compliance concerns | Public-source disclaimers, audit IDs, legal review |
| Subscription complexity | Checkout friction | Start with simple geography-based tiers |

## 10. Change Control

Any material change to geography, data source, monetization model, alert channel, user segment, or state expansion should be handled as a change request. The change request should include business rationale, engineering impact, timeline impact, cost impact, and revised acceptance criteria.
