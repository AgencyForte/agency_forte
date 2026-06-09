CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'threat_event_type') THEN
    CREATE TYPE threat_event_type AS ENUM (
      'NEW_MARKET_ENTRY',
      'CARRIER_LAND_GRAB',
      'COMPETITOR_BLEEDING',
      'TRAPPED_TALENT_IDENTIFIED',
      'LOB_ENCROACHMENT'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'review_status') THEN
    CREATE TYPE review_status AS ENUM (
      'pending_review',
      'approved',
      'rejected',
      'suppressed_by_rule',
      'quarantined'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pipeline_run_status') THEN
    CREATE TYPE pipeline_run_status AS ENUM (
      'running',
      'succeeded',
      'failed',
      'quarantined'
    );
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS master_agencies (
  agency_tdi_id TEXT PRIMARY KEY,
  agency_npn TEXT,
  agency_ein TEXT,
  name TEXT NOT NULL,
  physical_city TEXT,
  physical_state TEXT,
  physical_zip TEXT,
  county TEXT,
  first_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  source_dataset TEXT NOT NULL DEFAULT '3yqc-fcdt',
  in_target_zone BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS master_agents (
  agent_npn TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  first_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  in_target_zone BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS master_agent_agency_links (
  agent_npn TEXT NOT NULL REFERENCES master_agents(agent_npn),
  agency_tdi_id TEXT NOT NULL REFERENCES master_agencies(agency_tdi_id),
  agency_ein TEXT,
  association_type TEXT NOT NULL,
  relationship_started_at DATE,
  first_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  last_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  structural_hash TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  confidence TEXT NOT NULL DEFAULT 'high',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (agent_npn, agency_tdi_id, association_type)
);

CREATE TABLE IF NOT EXISTS master_agency_appointments (
  agency_tdi_id TEXT NOT NULL REFERENCES master_agencies(agency_tdi_id),
  agency_ein TEXT,
  carrier_naic TEXT NOT NULL,
  carrier_name TEXT NOT NULL,
  appointment_type TEXT,
  effective_date DATE,
  first_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  last_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  structural_hash TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (agency_tdi_id, carrier_naic, appointment_type)
);

CREATE TABLE IF NOT EXISTS master_agent_appointments (
  agent_npn TEXT NOT NULL REFERENCES master_agents(agent_npn),
  carrier_naic TEXT NOT NULL,
  carrier_name TEXT NOT NULL,
  appointment_type TEXT,
  effective_date DATE,
  first_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  last_seen_date DATE NOT NULL DEFAULT CURRENT_DATE,
  structural_hash TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (agent_npn, carrier_naic, appointment_type)
);

CREATE TABLE IF NOT EXISTS market_timeline (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  event_type threat_event_type NOT NULL,
  review_status review_status NOT NULL DEFAULT 'pending_review',
  target_agency_id TEXT REFERENCES master_agencies(agency_tdi_id),
  target_agent_npn TEXT REFERENCES master_agents(agent_npn),
  carrier_naic TEXT,
  carrier_name TEXT,
  event_zip TEXT,
  event_county TEXT,
  confidence TEXT NOT NULL DEFAULT 'high',
  event_fingerprint TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL DEFAULT '{}'::JSONB,
  is_processed BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suppressed_severances (
  suppression_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  agent_npn TEXT NOT NULL,
  agency_tdi_id TEXT NOT NULL,
  association_type TEXT NOT NULL,
  relationship_started_at DATE,
  relationship_ended_at DATE NOT NULL DEFAULT CURRENT_DATE,
  tenure_months INTEGER,
  suppression_reason TEXT NOT NULL,
  structural_hash TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (structural_hash, relationship_ended_at)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  status pipeline_run_status NOT NULL DEFAULT 'running',
  row_delta INTEGER,
  event_count INTEGER NOT NULL DEFAULT 0,
  suppressed_count INTEGER NOT NULL DEFAULT 0,
  message TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
  logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS pipeline_anomalies (
  anomaly_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES pipeline_runs(run_id) ON DELETE SET NULL,
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  anomaly_type TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'warning',
  message TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
  is_resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS texas_zip_geo (
  zip TEXT PRIMARY KEY,
  county TEXT,
  centroid GEOGRAPHY(POINT, 4326),
  geometry GEOMETRY(MULTIPOLYGON, 4326),
  source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_agencies (
  agency_tdi_id TEXT,
  agency_npn TEXT,
  agency_ein TEXT,
  name TEXT,
  agency_type TEXT,
  license_type TEXT,
  qualification TEXT,
  license_issue_date DATE,
  expiration_date DATE,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  county TEXT
);

CREATE TABLE IF NOT EXISTS stage_agent_agency_links (
  agent_npn TEXT,
  agent_name TEXT,
  agency_tdi_id TEXT,
  agency_ein TEXT,
  agency_name TEXT,
  association_type TEXT,
  relationship_started_at DATE,
  confidence TEXT,
  structural_hash TEXT
);

CREATE TABLE IF NOT EXISTS stage_agency_appointments (
  agency_tdi_id TEXT,
  agency_ein TEXT,
  agency_name TEXT,
  carrier_naic TEXT,
  carrier_name TEXT,
  appointment_type TEXT,
  effective_date DATE,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  structural_hash TEXT
);

CREATE TABLE IF NOT EXISTS stage_agent_appointments (
  agent_npn TEXT,
  agent_name TEXT,
  carrier_naic TEXT,
  carrier_name TEXT,
  appointment_type TEXT,
  effective_date DATE,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  structural_hash TEXT
);

CREATE TABLE IF NOT EXISTS carrier_to_line_matrix (
  carrier_naic TEXT PRIMARY KEY,
  carrier_name TEXT NOT NULL,
  line_of_business TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_master_agencies_zip ON master_agencies(physical_zip);
CREATE INDEX IF NOT EXISTS idx_master_links_agency ON master_agent_agency_links(agency_tdi_id);
CREATE INDEX IF NOT EXISTS idx_master_links_active ON master_agent_agency_links(is_active);
CREATE INDEX IF NOT EXISTS idx_market_timeline_detected ON market_timeline(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_timeline_type ON market_timeline(event_type);
CREATE INDEX IF NOT EXISTS idx_market_timeline_review ON market_timeline(review_status);
CREATE INDEX IF NOT EXISTS idx_suppressed_severances_detected ON suppressed_severances(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_anomalies_detected ON pipeline_anomalies(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_texas_zip_geo_centroid ON texas_zip_geo USING GIST(centroid);
CREATE INDEX IF NOT EXISTS idx_master_agencies_target_zone ON master_agencies(in_target_zone) WHERE in_target_zone = TRUE;
CREATE INDEX IF NOT EXISTS idx_master_agents_target_zone ON master_agents(in_target_zone) WHERE in_target_zone = TRUE;

