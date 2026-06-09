import { createClient, type SupabaseClient } from "@supabase/supabase-js";

export type SupabaseAdminState =
  | { configured: true; client: SupabaseClient }
  | { configured: false; missing: string[] };

export function getSupabaseAdmin(): SupabaseAdminState {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const missing = [
    ["NEXT_PUBLIC_SUPABASE_URL", url],
    ["SUPABASE_SERVICE_ROLE_KEY", serviceRoleKey]
  ]
    .filter(([, value]) => !value)
    .map(([key]) => key as string);

  if (missing.length > 0) {
    return { configured: false, missing };
  }

  return {
    configured: true,
    client: createClient(url as string, serviceRoleKey as string, {
      auth: { persistSession: false }
    })
  };
}
