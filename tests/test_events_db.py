import pytest
import polars as pl
from insuretra_pipeline.db import consolidate_master_sql, generate_events_sql, process_events_geo, reset_staging_and_load

def test_competitor_bleeding_and_market_arbitrage(db_connection):
    """Test Cases 4.1 & 4.2"""
    # Seed master_agents and master_agencies
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name) VALUES ('npn:ag1', 'Agency 1'), ('npn:ag2', 'Agency 2') ON CONFLICT DO NOTHING")
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name) VALUES ('9001', 'Agent 1'), ('9002', 'Agent 2') ON CONFLICT DO NOTHING")
    
    # Seed carrier for departing agent
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, appointment_type, is_active, structural_hash)
        VALUES ('9001', 'C_DEP', 'Departing Carrier', 'Life', TRUE, 'hash_app_1')
    """)

    # 4.1 Competitor bleeding: Agent was in master for 36+ months, but not in staging
    db_connection.execute("""
        INSERT INTO master_agent_agency_links (agent_npn, agency_tdi_id, association_type, relationship_started_at, structural_hash, is_active)
        VALUES ('9001', 'npn:ag1', 'Sub-Agent', CURRENT_DATE - INTERVAL '37 months', 'hash_bleed_1', TRUE)
    """)
    
    # 4.1b Competitor bleeding (Carrier Pull-out): Agency lost an appointment (24+ months tenure)
    db_connection.execute("""
        INSERT INTO master_agency_appointments (agency_tdi_id, carrier_naic, carrier_name, appointment_type, is_active, structural_hash, effective_date)
        VALUES ('npn:ag1', 'C_LOST', 'Lost Carrier', 'PNC', TRUE, 'hash_lost_1', CURRENT_DATE - INTERVAL '25 months')
    """)


    generate_events_sql(db_connection)
    db_connection.commit()
    
    events = db_connection.execute("SELECT event_type, target_agent_npn, target_agency_id, payload FROM market_timeline").fetchall()
    
    # Assert Agent Bleeding (36+ months)
    agent_bleed = next((e for e in events if e["event_type"] == "COMPETITOR_BLEEDING" and e["target_agent_npn"] == "9001"), None)
    assert agent_bleed is not None
    assert "departing_carriers" in agent_bleed["payload"]
    assert agent_bleed["payload"]["departing_carriers"][0]["carrier_naic"] == "C_DEP"

    # Assert Carrier Pull-out Bleeding
    carrier_bleed = next((e for e in events if e["event_type"] == "COMPETITOR_BLEEDING" and e["target_agent_npn"] is None and e["target_agency_id"] == "npn:ag1"), None)
    assert carrier_bleed is not None
    assert carrier_bleed["payload"]["source_rule"] == "agency_lost_carrier"

    assert "COMPETITOR_BLEEDING" in event_types

def test_lob_encroachment_and_geo_routing(db_connection):
    """Test Cases 4.3 & 5.1"""
    # Seed LOB matrix
    db_connection.execute("""
        INSERT INTO carrier_to_line_matrix (carrier_naic, carrier_name, line_of_business)
        VALUES ('C_PNC', 'PNC Carrier', 'Property and Casualty') ON CONFLICT DO NOTHING
    """)
    
    # Veteran agent (in master > 3 years)
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name, first_seen_date) VALUES ('9003', 'Veteran', CURRENT_DATE - INTERVAL '4 years') ON CONFLICT DO NOTHING")
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name) VALUES ('npn:ag3', 'Agency 3') ON CONFLICT DO NOTHING")
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, structural_hash, is_active)
        VALUES ('9003', 'C_PNC', 'PNC Carrier', 'h_vet_pnc', TRUE)
    """)
    
    # Hire veteran
    db_connection.execute("""
        INSERT INTO stage_agent_agency_links (agent_npn, agency_tdi_id, association_type, structural_hash)
        VALUES ('9003', 'npn:ag3', 'Sub-Agent', 'hash_lob_1')
    """)
    
    generate_events_sql(db_connection)
    db_connection.commit()
    
    # Check for LOB_ENCROACHMENT
    events = db_connection.execute("SELECT event_type, payload FROM market_timeline WHERE target_agent_npn = '9003'").fetchall()
    assert len(events) == 1
    assert events[0]["event_type"] == "LOB_ENCROACHMENT"
    assert "Property and Casualty" in events[0]["payload"]["lines_overlapped"]
    
    # Test Geo-Routing (5.1)
    # Seed geo zip
    db_connection.execute("""
        INSERT INTO texas_zip_geo (zip, centroid, geometry) 
        VALUES ('78701', ST_SetSRID(ST_MakePoint(-97.7431, 30.2672), 4326), ST_SetSRID(ST_MakePoint(-97.7431, 30.2672), 4326))
        ON CONFLICT DO NOTHING
    """)
    # Set event zip
    db_connection.execute("UPDATE market_timeline SET event_zip = '78701' WHERE event_type = 'LOB_ENCROACHMENT'")
    
    process_events_geo(db_connection)
    db_connection.commit()
    
    processed = db_connection.execute("SELECT is_processed, payload FROM market_timeline WHERE event_type = 'LOB_ENCROACHMENT'").fetchone()
    assert processed["is_processed"] is True
    assert processed["payload"]["geo_routing"]["processed"] is True
    assert processed["payload"]["geo_routing"]["zip"] == "78701"
