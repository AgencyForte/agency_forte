import { getSupabaseAdmin } from "./supabase-admin";

export type QueryResult<T> =
  | { configured: true; rows: T[]; error?: string }
  | { configured: false; missing: string[]; rows: T[] };

async function queryTable<T>(table: string, orderColumn: string, limit = 50): Promise<QueryResult<T>> {
  const supabase = getSupabaseAdmin();
  if (!supabase.configured) {
    return { configured: false, missing: supabase.missing, rows: [] };
  }

  const { data, error } = await supabase.client
    .from(table)
    .select("*")
    .order(orderColumn, { ascending: false })
    .limit(limit);

  return {
    configured: true,
    rows: (data ?? []) as T[],
    error: error?.message
  };
}

export type PipelineRun = {
  run_id: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  row_delta: number | null;
  event_count: number | null;
  suppressed_count: number | null;
};

export type MarketEvent = {
  event_id: string;
  detected_at: string;
  event_type: string;
  review_status: string;
  target_agency_id: string | null;
  target_agent_npn: string | null;
  carrier_naic: string | null;
  carrier_name: string | null;
  event_zip: string | null;
  event_county: string | null;
  confidence: string | null;
  payload?: any;
  is_processed: boolean;
};

export type SuppressedSeverance = {
  suppression_id: string;
  detected_at: string;
  agent_npn: string;
  agency_tdi_id: string;
  relationship_started_at: string | null;
  relationship_ended_at: string;
  tenure_months: number | null;
  suppression_reason: string;
};

export type PipelineAnomaly = {
  anomaly_id: string;
  detected_at: string;
  anomaly_type: string;
  severity: string;
  message: string;
};

export const getPipelineRuns = () => queryTable<PipelineRun>("pipeline_runs", "started_at");
export const getMarketEvents = () => queryTable<MarketEvent>("market_timeline", "detected_at");
export const getSuppressedSeverances = () =>
  queryTable<SuppressedSeverance>("suppressed_severances", "detected_at");
export const getPipelineAnomalies = () => queryTable<PipelineAnomaly>("pipeline_anomalies", "detected_at");

export async function getMarketEventById(eventId: string): Promise<{ configured: boolean; missing?: string[]; row: MarketEvent | null; error?: string }> {
  const supabase = getSupabaseAdmin();
  if (!supabase.configured) {
    return { configured: false, missing: supabase.missing, row: null };
  }

  const { data, error } = await supabase.client
    .from("market_timeline")
    .select("*")
    .eq("event_id", eventId)
    .single();

  return {
    configured: true,
    row: (data ?? null) as MarketEvent | null,
    error: error?.message
  };
}
