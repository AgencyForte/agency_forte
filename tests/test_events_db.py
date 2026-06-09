import pytest
import polars as pl
from insuretra_pipeline.db import consolidate_master_sql, generate_events_sql, process_events_geo, reset_staging_and_load

@pytest.fixture(autouse=True)
def run_around_tests(db_connection):
    # Wrap each test in a transaction to roll back changes and maintain untainted live metadata
    with db_connection.transaction():
        yield db_connection
        db_connection.rollback()

def test_dual_entity_competitor_bleeding(db_connection):
    """
    Dual-Entity Framework: Competitor Bleeding Alert (Offense)
    """
    # 1. Entity A (Tenant Buyer)
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:buyer_1', 'Buyer Agency', '77002') ON CONFLICT DO NOTHING")
    
    # 2. Entity B (Target Competitor) in IDENTICAL ZIP
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:comp_1', 'Competitor Agency', '77002') ON CONFLICT DO NOTHING")
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name) VALUES ('9001', 'Exiting Producer') ON CONFLICT DO NOTHING")
    
    # Seed carrier for departing agent
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, appointment_type, is_active, structural_hash)
        VALUES ('9001', 'C_DEP', 'Departing Carrier', 'Life', TRUE, 'hash_app_1')
    """)

    # Competitor bleeding: Agent was in master for 36+ months, but not in staging (Producer Exit)
    db_connection.execute("""
        INSERT INTO master_agent_agency_links (agent_npn, agency_tdi_id, association_type, relationship_started_at, structural_hash, is_active)
        VALUES ('9001', 'npn:comp_1', 'Sub-Agent', CURRENT_DATE - INTERVAL '37 months', 'hash_bleed_1', TRUE)
    """)
    
    # Generate global events
    generate_events_sql(db_connection)
    
    # Fetch Buyer Alerts using the new RPC
    events = db_connection.execute("SELECT * FROM get_buyer_alerts('npn:buyer_1')").fetchall()
    
    # Assert
    agent_bleed = next((e for e in events if e["event_type"] == "COMPETITOR_BLEEDING" and e["target_agent_npn"] == "9001"), None)
    assert agent_bleed is not None, "COMPETITOR_BLEEDING event was not routed to the Buyer in the identical ZIP code."
    assert agent_bleed["payload"]["agency_name"] == "Competitor Agency"
    assert agent_bleed["payload"]["agent_name"] == "Exiting Producer"
    assert agent_bleed["payload"]["tenure_months"] == 37


def test_dual_entity_market_arbitrage(db_connection):
    """
    Dual-Entity Framework: Market Access Arbitrage (Recruitment)
    """
    # 1. Entity A (Tenant Buyer)
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, county) VALUES ('npn:buyer_arb', 'Buyer Arb', 'Harris') ON CONFLICT DO NOTHING")
    # Assign premium carrier to Buyer
    db_connection.execute("""
        INSERT INTO master_agency_appointments (agency_tdi_id, carrier_naic, carrier_name, is_active, structural_hash)
        VALUES ('npn:buyer_arb', '24082', 'Ohio Security Ins Co', TRUE, 'hash_arb_buyer_app')
    """)

    # 2. Entity B (Competitor) lacking appointment
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, county) VALUES ('npn:comp_arb', 'Competitor Arb', 'Harris') ON CONFLICT DO NOTHING")
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name) VALUES ('arb_producer', 'Trapped Producer') ON CONFLICT DO NOTHING")
    
    # Attach veteran producer to Competitor
    db_connection.execute("""
        INSERT INTO master_agent_agency_links (agent_npn, agency_tdi_id, association_type, structural_hash, is_active)
        VALUES ('arb_producer', 'npn:comp_arb', 'Sub-Agent', 'hash_arb_link', TRUE)
    """)
    # Producer has the premium appointment individually
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, is_active, structural_hash)
        VALUES ('arb_producer', '24082', 'Ohio Security Ins Co', TRUE, 'hash_arb_prod_app')
    """)

    # Fetch Arbitrage targets
    targets = db_connection.execute("SELECT * FROM get_market_access_arbitrage('npn:buyer_arb')").fetchall()
    
    # Assert
    assert len(targets) == 1, "Expected exactly 1 trapped talent target."
    assert targets[0]["target_agent_npn"] == "arb_producer"
    assert targets[0]["competitor_agency_id"] == "npn:comp_arb"
    # Verify the payload returns the exact producer profile to the Buyer's dashboard view
    missing_carriers = targets[0]["missing_buyer_carriers"]
    assert len(missing_carriers) == 1
    assert missing_carriers[0]["carrier_naic"] == "24082"


def test_dual_entity_lob_encroachment_suppression(db_connection):
    """
    Dual-Entity Framework: LOB Encroachment Alert (Defense) and Suppression Rules
    """
    # Seed LOB matrix
    db_connection.execute("""
        INSERT INTO carrier_to_line_matrix (carrier_naic, carrier_name, line_of_business)
        VALUES ('C_AUTO', 'Auto Carrier', 'Commercial Auto'),
               ('C_HOME', 'Home Carrier', 'Homeowners') ON CONFLICT DO NOTHING
    """)

    # 1. Entity A (Tenant Buyer) holds Commercial Auto
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:buyer_lob', 'Buyer LOB', '78701') ON CONFLICT DO NOTHING")
    db_connection.execute("""
        INSERT INTO master_agency_appointments (agency_tdi_id, carrier_naic, carrier_name, is_active, structural_hash)
        VALUES ('npn:buyer_lob', 'C_AUTO', 'Auto Carrier', TRUE, 'hash_buyer_auto')
    """)

    # 2. Entity B (Competitor) hires a veteran
    db_connection.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:comp_lob', 'Competitor LOB', '78701') ON CONFLICT DO NOTHING")
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name, first_seen_date) VALUES ('vet_1', 'Auto Veteran', CURRENT_DATE - INTERVAL '4 years') ON CONFLICT DO NOTHING")
    
    # Veteran 1 writes Commercial Auto (OVERLAPPING)
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, is_active, structural_hash)
        VALUES ('vet_1', 'C_AUTO', 'Auto Carrier', TRUE, 'hash_vet1_auto')
    """)
    # Hire Veteran 1
    db_connection.execute("""
        INSERT INTO stage_agent_agency_links (agent_npn, agency_tdi_id, association_type, structural_hash)
        VALUES ('vet_1', 'npn:comp_lob', 'Sub-Agent', 'hash_lob_link1')
    """)

    # 3. Competitor hires a SECOND veteran who writes Homeowners (NO OVERLAP)
    db_connection.execute("INSERT INTO master_agents (agent_npn, full_name, first_seen_date) VALUES ('vet_2', 'Home Veteran', CURRENT_DATE - INTERVAL '4 years') ON CONFLICT DO NOTHING")
    db_connection.execute("""
        INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, is_active, structural_hash)
        VALUES ('vet_2', 'C_HOME', 'Home Carrier', TRUE, 'hash_vet2_home')
    """)
    # Hire Veteran 2
    db_connection.execute("""
        INSERT INTO stage_agent_agency_links (agent_npn, agency_tdi_id, association_type, structural_hash)
        VALUES ('vet_2', 'npn:comp_lob', 'Sub-Agent', 'hash_lob_link2')
    """)

    # Generate Events
    generate_events_sql(db_connection)
    
    # Fetch alerts for Buyer
    alerts = db_connection.execute("SELECT * FROM get_buyer_alerts('npn:buyer_lob') WHERE event_type = 'LOB_ENCROACHMENT'").fetchall()
    
    # Assertions
    # The engine should silently suppress 'vet_2' because Homeowners does not overlap with the Buyer's Commercial Auto portfolio.
    assert len(alerts) == 1, "Expected exactly 1 unsuppressed LOB_ENCROACHMENT alert."
    assert alerts[0]["target_agent_npn"] == "vet_1", "The overlapping Commercial Auto veteran should trigger an alert."
    assert alerts[0]["payload"]["agent_name"] == "Auto Veteran"
    
    # Critical Fix (Data Integrity): Ensure historical_carriers matches Commercial Auto
    historical = alerts[0]["payload"]["historical_carriers"]
    assert len(historical) == 1
    assert historical[0]["line_of_business"] == "Commercial Auto"
