import psycopg
import json
from insuretra_pipeline.config import get_settings
from insuretra_pipeline.db import connect, generate_events_sql

def run_dual_entity_simulation():
    settings = get_settings()
    if not settings.database_url:
        print("DATABASE_URL not set. Cannot run simulation.")
        return
        
    print("Starting Dual-Entity Live Simulation...")
    
    with connect(settings.database_url) as conn:
        with conn.transaction():
            print("Seeding Dual-Entity Base State...")
            # Entity A: Tenant Buyer
            conn.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:sim_buyer', 'Simulation Buyer Agency', '78701') ON CONFLICT DO NOTHING")
            
            # Entity B: Target Competitor
            conn.execute("INSERT INTO master_agencies (agency_tdi_id, name, physical_zip) VALUES ('npn:sim_comp', 'Simulation Competitor', '78701') ON CONFLICT DO NOTHING")
            conn.execute("INSERT INTO master_agents (agent_npn, full_name) VALUES ('sim_prod_1', 'Exiting Producer') ON CONFLICT DO NOTHING")
            
            # Seed carrier for departing agent
            conn.execute("""
                INSERT INTO master_agent_appointments (agent_npn, carrier_naic, carrier_name, appointment_type, is_active, structural_hash)
                VALUES ('sim_prod_1', '10052', 'Chubb', 'Life', TRUE, 'hash_sim_app_1')
            """)

            # Competitor bleeding: Agent was in master for 36+ months, but not in staging (Producer Exit)
            conn.execute("""
                INSERT INTO master_agent_agency_links (agent_npn, agency_tdi_id, association_type, relationship_started_at, structural_hash, is_active)
                VALUES ('sim_prod_1', 'npn:sim_comp', 'Sub-Agent', CURRENT_DATE - INTERVAL '37 months', 'sim_hash_bleed', TRUE)
            """)
            
            print("Running Pipeline Engine (generate_events_sql)...")
            generate_events_sql(conn)
            
            print("Executing Buyer-Centric Filtering via get_buyer_alerts RPC...")
            events = conn.execute("SELECT event_type, payload FROM get_buyer_alerts('npn:sim_buyer') WHERE target_agent_npn = 'sim_prod_1'").fetchall()
            
            print("\n[Simulation Results for Buyer: npn:sim_buyer]")
            if not events:
                print("No alerts found. (Suppressed or Missing)")
            else:
                for event in events:
                    print(f"Alert: {event['event_type']}")
                    print(json.dumps(event['payload'], indent=2))
            
            print("\nRolling back transaction to keep DB untainted...")
            conn.rollback()

if __name__ == '__main__':
    run_dual_entity_simulation()
