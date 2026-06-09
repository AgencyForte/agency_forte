CREATE OR REPLACE FUNCTION get_market_access_arbitrage(p_buyer_agency_id text)
RETURNS TABLE (
    target_agent_npn varchar,
    agent_name varchar,
    competitor_agency_id varchar,
    competitor_agency_name varchar,
    missing_buyer_carriers jsonb,
    agent_total_carriers bigint
) AS $$
BEGIN
    RETURN QUERY
    WITH buyer_carriers AS (
        SELECT carrier_naic, carrier_name
        FROM master_agency_appointments
        WHERE agency_tdi_id = p_buyer_agency_id AND is_active
    ),
    buyer_county AS (
        SELECT county FROM master_agencies WHERE agency_tdi_id = p_buyer_agency_id LIMIT 1
    ),
    competitors AS (
        SELECT agency_tdi_id, name, county
        FROM master_agencies
        WHERE county = (SELECT county FROM buyer_county)
          AND agency_tdi_id != p_buyer_agency_id
    ),
    competitor_missing_carriers AS (
        SELECT 
            c.agency_tdi_id,
            jsonb_agg(jsonb_build_object('carrier_naic', bc.carrier_naic, 'carrier_name', bc.carrier_name)) as missing_carriers
        FROM competitors c
        CROSS JOIN buyer_carriers bc
        LEFT JOIN master_agency_appointments ca 
            ON ca.agency_tdi_id = c.agency_tdi_id 
            AND ca.carrier_naic = bc.carrier_naic 
            AND ca.is_active
        WHERE ca.carrier_naic IS NULL
        GROUP BY c.agency_tdi_id
    )
    SELECT
        l.agent_npn,
        a.full_name AS agent_name,
        c.agency_tdi_id AS competitor_agency_id,
        c.name AS competitor_agency_name,
        cmc.missing_carriers AS missing_buyer_carriers,
        (SELECT COUNT(*) FROM master_agent_appointments map WHERE map.agent_npn = l.agent_npn AND map.is_active) AS agent_total_carriers
    FROM competitor_missing_carriers cmc
    JOIN competitors c ON c.agency_tdi_id = cmc.agency_tdi_id
    JOIN master_agent_agency_links l ON l.agency_tdi_id = c.agency_tdi_id AND l.is_active AND LOWER(l.association_type) = 'sub-agent'
    JOIN master_agents a ON a.agent_npn = l.agent_npn
    WHERE (SELECT COUNT(*) FROM master_agent_appointments map WHERE map.agent_npn = l.agent_npn AND map.is_active) >= 3;
END;
$$ LANGUAGE plpgsql STABLE;
