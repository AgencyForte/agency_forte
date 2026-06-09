# Human-In-The-Loop Interface: Texas Agency Intelligence Engine

## 1. Purpose

This document defines the human actions, decisions, approvals, review queues, and escalation questions required to operate and launch the V1 Texas Agency Intelligence Engine.

The product is data-driven and automated, but V1 must include deliberate human oversight at critical points because the system converts public regulatory data into competitive business intelligence. Human review protects customers from false positives, prevents commercially weak alerts, supports compliance, and creates a feedback loop for improving the intelligence engine.

V1 remains a SaaS-only product. Programmatic SEO, public-facing agency pages, sitemaps, canonical routes, and indexable profile metadata are not part of this human-in-the-loop process for V1.

## 2. Human Roles

### Product Owner

Required actions:

- Approve MVP scope and acceptance criteria.
- Approve dashboard, profile, alert, and export user experience.
- Review representative generated events before beta.
- Approve beta release.
- Approve production launch.

Questions owned:

- Does this alert create a clear business action for an agency owner?
- Is this intelligence valuable enough to show in the SaaS product?
- Should an ambiguous event be suppressed, shown, or reclassified?

### Business Development

Required actions:

- Confirm subscription tiers: ZIP, county, regional, or other packaging.
- Confirm plan names, pricing, trial length, and checkout rules.
- Confirm export pack names, pricing, and included fields.
- Approve customer-facing value propositions and alert framing.
- Confirm initial beta customer profile and sales/onboarding process.

Questions owned:

- Which customer segment gets priority for beta?
- What geography package is easiest to sell first?
- Which export has the strongest immediate willingness to pay?
- What wording best communicates offensive market intelligence without overpromising real-time accuracy?

### Domain Expert

Required actions:

- Review sample Competitor Bleeding, Carrier Land-Grab, New Market Entry, and Market Access Arbitrage events.
- Validate carrier importance assumptions.
- Validate whether sample trapped talent records are commercially plausible.
- Review the 24-month Competitor Bleeding tenure filter against real examples.
- Identify common false-positive patterns.

Questions owned:

- Would an agency owner care about this event?
- Is this carrier meaningful in the relevant market?
- Does this producer movement likely indicate opportunity, noise, or administrative cleanup?
- Should certain carrier or agency types be excluded from alerts?

### Compliance / Legal Reviewer

Required actions:

- Approve data-use disclaimers.
- Approve alert and paywall copy.
- Review data provenance language.
- Review export content and field inclusion.
- Approve privacy and terms language before launch.

Questions owned:

- Is the product accurately representing public-data limitations?
- Are we implying employment facts that the source data does not prove?
- Are user-facing claims framed as detected regulatory relationship changes rather than guaranteed real-world activity?
- Are exports and alerts acceptable under the planned terms of service?

### Technical Lead

Required actions:

- Approve data contracts and schema.
- Approve anomaly thresholds and dump guard behavior.
- Review pipeline logs and suppressed-event logs during beta.
- Approve production readiness.
- Own incident triage for data and system failures.

Questions owned:

- Is this event reproducible from source data?
- Did the pipeline produce this event for the right reason?
- Is the system suppressing short-tenure severances correctly?
- Should the dump guard threshold be adjusted?

### QA Reviewer

Required actions:

- Validate test fixtures for each event type.
- Execute manual end-to-end tests.
- Confirm paywall and entitlement behavior.
- Confirm alert routing behavior.
- Confirm export download behavior.

Questions owned:

- Can a user access only what their subscription permits?
- Are suppressed Competitor Bleeding records hidden from all user-facing surfaces?
- Are alerts delivered only to users watching the affected geography?

### Operations Owner

Required actions:

- Monitor production pipeline runs.
- Review operational alerts.
- Escalate endpoint failures, schema changes, bulk-update quarantines, and abnormal event volume.
- Confirm backups and incident response process.

Questions owned:

- Is the nightly run healthy?
- Did TDI source behavior change?
- Does an anomaly need engineering review before master state is updated?

## 3. Human Review Gates by Project Phase

| Phase | Human Gate | Required Human Action | Owner |
| --- | --- | --- | --- |
| Phase 0: Discovery | Source and commercial assumptions | Approve endpoint inventory, service accounts, pricing placeholders, and packaging assumptions | Product Owner, Business Development, Technical Lead |
| Phase 1: Data Foundation | Schema readiness | Approve tables, tenure metadata, suppressed severance logs, geography source, and audit fields | Technical Lead |
| Phase 2: Pipeline MVP | Pipeline dry-run review | Review sample ingestion, diff output, dump guard behavior, and logs | Technical Lead, QA Reviewer |
| Phase 3: Intelligence and Geo Routing | Event quality review | Review samples for all four event types before customer exposure | Product Owner, Domain Expert |
| Phase 4: SaaS Core | UX review | Approve onboarding, dashboard, agency profile, event detail, and admin views | Product Owner |
| Phase 5: Monetization | Commercial approval | Approve Stripe products, export packs, trial behavior, and paid-field gating | Business Development, Product Owner |
| Phase 6: SaaS Hardening | Entitlement and suppression review | Verify access control, alert routing, and 24-month filter behavior | QA Reviewer, Technical Lead |
| Phase 7: Beta | Beta release approval | Approve beta cohort, known issues, and support process | Product Owner, Business Development |
| Phase 8: Launch | Production launch approval | Approve launch checklist, compliance language, monitoring, and smoke test results | Product Owner, Compliance, Technical Lead |

## 4. Human Review Queues

### Event Quality Review Queue

Purpose:

- Validate that generated intelligence events are commercially useful and correctly classified.

Records included:

- Newly generated `COMPETITOR_BLEEDING` events.
- Newly generated `CARRIER_LAND_GRAB` events.
- Newly generated `NEW_MARKET_ENTRY` events.
- Newly generated `TRAPPED_TALENT_IDENTIFIED` candidates.
- Representative non-alerted records used for quality comparison.

Required reviewer action:

- Mark each reviewed event as `approved`, `rejected`, `needs_investigation`, or `rule_change_candidate`.
- Add a short reason for rejected or ambiguous events.
- Identify whether the issue is source-data quality, business irrelevance, geography mismatch, carrier ranking, tenure logic, or copy risk.

Escalation questions:

- Is this a real structural change or a likely administrative artifact?
- Is the event valuable enough to alert a paying customer?
- Should this event type require a stronger confidence threshold?
- Should this agency, carrier, or relationship type be excluded?

### Suppressed Severance Review Queue

Purpose:

- Audit severed agent-agency relationships that fail the 24-month tenure filter.

Records included:

- Agent-agency severances under 24 months.
- Calculated tenure duration.
- Agency ID, agent NPN, relationship dates, detected date, ZIP/county where available.
- Suppression reason.

Required reviewer action:

- Review samples during beta and early production.
- Confirm suppressed records are not visible in alerts, dashboards, or competitor bleeding exports.
- Identify patterns where the tenure threshold may be too strict or too loose.

Escalation questions:

- Are important producer movements being suppressed?
- Are short-tenure movements mostly low-value noise?
- Should the tenure threshold remain 24 months for all agencies, or vary by producer/carrier context in V2?

### Administrative Dump Guard Queue

Purpose:

- Review suspected statewide administrative updates or carrier migrations before they pollute user-facing intelligence.

Records included:

- Pipeline run ID.
- Row deltas by dataset.
- Threshold breached.
- Source endpoint affected.
- Master-state update action.
- Event-generation suppression status.

Required reviewer action:

- Confirm whether quarantine behavior was appropriate.
- Approve master-state update if manual approval is configured.
- Request threshold adjustment if repeated false quarantines occur.

Escalation questions:

- Did TDI publish a schema or data migration?
- Did a major carrier update many appointments at once?
- Should event generation remain suppressed for this run?
- Is a customer-facing data freshness notice required?

### Alert Copy Review Queue

Purpose:

- Ensure generated alerts are useful, accurate, and not overstated.

Records included:

- Event type.
- Raw source identifiers.
- Plain-English summary.
- Geography.
- Call to action.
- Data freshness note.

Required reviewer action:

- Approve alert templates before beta.
- Review a sample of generated alerts before launch.
- Confirm copy does not imply unsupported employment or intent claims.

Escalation questions:

- Does the copy clearly say what changed in public records?
- Does the copy overstate certainty?
- Does the recommended action match the intelligence?

### Export Review Queue

Purpose:

- Validate paid CSV exports before customer delivery, especially during beta.

Records included:

- Export type.
- Geography.
- Included fields.
- Row count.
- Data provenance fields.
- Purchase/user association.

Required reviewer action:

- Confirm export contains only approved fields.
- Confirm row counts are plausible.
- Confirm the export respects geography and entitlement boundaries.
- Approve beta export samples before customer delivery.

Escalation questions:

- Are NPNs, carrier names, and agency IDs appropriate for this export?
- Does the export include suppressed Competitor Bleeding records by mistake?
- Should a field be removed or renamed for compliance or commercial clarity?

## 5. Human Decisions Required Before Build

The following decisions are required before engineering can complete V1 without avoidable rework.

| Decision | Owner | Required Answer |
| --- | --- | --- |
| Subscription geography tiers | Business Development | Confirm ZIP, county, regional, or revised tier structure |
| Pricing and trial length | Business Development | Confirm initial plan prices and trial rules |
| Export pack packaging | Business Development | Confirm first export products, prices, and included geographies |
| Carrier importance list | Domain Expert | Provide initial high-value carrier ranking or approve manual seed list |
| Alert tone | Product Owner, Compliance | Approve aggressive/offensive wording boundaries |
| Legal disclaimers | Compliance | Approve data freshness, public-source, and limitation language |
| Beta customer cohort | Business Development | Identify first users and monitored geographies |
| Support channel | Product Owner | Confirm who receives customer support questions during beta |
| Operational alert channel | Technical Lead | Confirm Slack or Discord destination |
| Launch approval authority | Product Owner | Name final approver for production launch |

## 6. Human Questions by Functional Area

### Data Source and Provenance

- Which exact TDI Socrata resource IDs are approved for production ingestion?
- Should we store raw source payload snapshots, or only normalized records and source IDs?
- How long should pipeline logs and suppressed severance logs be retained?
- What data freshness disclaimer should appear in the product?

### Competitor Bleeding

- Is 24 months the correct universal tenure threshold for V1?
- Should the tenure clock use source effective date, first-seen date, or the earlier reliable date?
- Should certain producer or agency types be excluded from Competitor Bleeding alerts?
- Should severed relationships under 24 months be available to admins only, or completely hidden except in pipeline logs?

### Market Access Arbitrage

- Which carriers indicate meaningful market access advantage?
- What makes a producer "trapped" in V1 without private production data?
- Should trapped talent exports include all candidate records or only high-confidence records?
- Are there any carrier or agency combinations that should be excluded from recruiting-oriented outputs?

### Carrier Land-Grab

- Which carriers should trigger high-priority alerts?
- Should every new carrier appointment create an event, or only carriers above a threshold?
- Should the system suppress new carrier appointments for agencies less than 30 days old?
- What customer action should each carrier alert recommend?

### New Market Entry

- What qualifies as a new market entry: new legal entity, new physical branch, new ZIP, or all three?
- Should agencies without reliable ZIP data be surfaced as lower-confidence events?
- Should new market entry alerts include all new agencies or only agencies within paid watch areas?

### Geography and Routing

- Should V1 use ZIP centroid radius matching, county matching, or both?
- How should events be routed when ZIP is missing but county is available?
- Should users be allowed to monitor multiple non-contiguous ZIP codes?
- What happens when an event overlaps multiple subscribers' geographies?

### Monetization

- Should exports be available only to subscribers, or also as standalone purchases?
- Should export purchases expire?
- Should failed subscriptions immediately revoke access or enter a grace period?
- Should beta users bypass Stripe, use coupons, or use live checkout?

### Compliance

- What disclaimers are required on event details, exports, and alerts?
- Can alert copy use terms like "producer left" or must it say "public records no longer show an active relationship"?
- Are there fields that should never be included in exports?
- What manual review is required before beta customer exposure?

## 7. Human Escalation Triggers

Immediate human review is required when:

- A pipeline run fails.
- A source endpoint changes schema.
- A row delta exceeds the dump guard threshold.
- Event volume is materially higher or lower than normal.
- An alert would affect an unusually large number of customers.
- The same agency produces repeated conflicting events.
- A customer challenges data accuracy.
- A paid export has an unexpected row count.
- A suppressed severance pattern suggests the 24-month filter is hiding high-value movements.
- A legal or compliance concern is raised about copy, data use, or export content.

## 8. Human Approval States

Recommended review statuses:

- `pending_review`: Awaiting human review.
- `approved`: Approved for user-facing display or delivery.
- `rejected`: Not suitable for user-facing display or delivery.
- `needs_investigation`: Requires technical or domain review.
- `suppressed_by_rule`: Automatically suppressed by approved business rule.
- `quarantined`: Held because of pipeline anomaly or dump guard.
- `approved_with_note`: Approved, but reviewer added caution or follow-up.

Recommended reviewer note fields:

- Reviewer name.
- Reviewed timestamp.
- Decision.
- Reason code.
- Free-form note.
- Follow-up owner.

## 9. Beta Operating Cadence

During beta, humans should review the system on a fixed cadence.

Daily:

- Review pipeline run status.
- Review operational anomalies.
- Review event volume by type.
- Review a sample of new user-facing events.
- Confirm no suppressed severances leaked into user-facing surfaces.

Twice weekly:

- Review customer feedback.
- Review alert usefulness with Business Development.
- Review export purchase or export request behavior.
- Review false-positive and false-negative examples.

Weekly:

- Adjust carrier ranking assumptions if needed.
- Review dump guard threshold behavior.
- Review pricing and packaging feedback.
- Decide whether any rule changes are needed before launch.

## 10. Launch Approval Checklist

Human launch approval requires:

- Product Owner approval of core workflows.
- Business Development approval of pricing, packaging, and beta/customer motion.
- Domain Expert approval of representative event quality.
- Compliance approval of alert, paywall, export, disclaimer, and data-use language.
- Technical Lead approval of pipeline, monitoring, backup, and production readiness.
- QA approval of access control, event routing, export delivery, and 24-month filter tests.
- Operations Owner approval of incident process and alert channels.

No production launch should occur until all launch approvers have either approved their area or recorded an accepted exception.

## 11. V2 Human Review Candidates

The following topics are intentionally deferred from V1 but should receive human review before V2 planning:

- Programmatic SEO and public-facing agency profile pages.
- Public obfuscated intelligence summaries.
- Sitemap and canonical routing strategy.
- Carrier scoring automation.
- AI-assisted playbook recommendations.
- CRM integrations.
- Direct-mail or ad campaign integrations.
- Multi-state expansion.
- Enterprise team accounts and custom pricing.

