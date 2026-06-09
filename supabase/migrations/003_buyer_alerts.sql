
CREATE OR REPLACE FUNCTION get_buyer_alerts(p_buyer_agency_id TEXT)
RETURNS SETOF market_timeline AS \$\$
BEGIN
  RETURN QUERY
  WITH buyer_geo AS (
    SELECT physical_zip, county
    FROM master_agencies
    WHERE agency_tdi_id = p_buyer_agency_id
  ),
  buyer_lines AS (
    SELECT DISTINCT cm.line_of_business
    FROM master_agency_appointments map
    JOIN carrier_to_line_matrix cm ON cm.carrier_naic = map.carrier_naic
    WHERE map.agency_tdi_id = p_buyer_agency_id AND map.is_active
  )
  SELECT mt.*
  FROM market_timeline mt
  CROSS JOIN buyer_geo bg
  WHERE mt.target_agency_id != p_buyer_agency_id
    AND (
      -- Rule 1: COMPETITOR_BLEEDING must be in the same ZIP code
      (mt.event_type = 'COMPETITOR_BLEEDING' AND mt.event_zip = bg.physical_zip)
      
      OR
      
      -- Rule 2: LOB_ENCROACHMENT must be in the same County (or ZIP) AND have overlapping lines of business
      (mt.event_type = 'LOB_ENCROACHMENT' AND mt.event_zip = bg.physical_zip AND EXISTS (
        SELECT 1
        FROM master_agent_appointments map
        JOIN carrier_to_line_matrix cm ON cm.carrier_naic = map.carrier_naic
        WHERE map.agent_npn = mt.target_agent_npn AND map.is_active
          AND cm.line_of_business IN (SELECT line_of_business FROM buyer_lines)
      ))

      OR

      -- Fallback: Other events in the same zip
      (mt.event_type NOT IN ('COMPETITOR_BLEEDING', 'LOB_ENCROACHMENT') AND mt.event_zip = bg.physical_zip)
    )
  ORDER BY mt.detected_at DESC;
END;
\$\$ LANGUAGE plpgsql STABLE;

