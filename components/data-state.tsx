import type { QueryResult } from "@/lib/admin-data";

export function DataState<T>({ result }: Readonly<{ result: QueryResult<T> }>) {
  if (!result.configured) {
    return (
      <div className="rounded-md border border-signal/30 bg-white p-4 text-sm text-ink">
        <p className="font-semibold">Supabase is not configured yet.</p>
        <p className="mt-1 text-black/70">Missing environment variables: {result.missing.join(", ")}</p>
      </div>
    );
  }

  if (result.error) {
    return (
      <div className="rounded-md border border-signal/30 bg-white p-4 text-sm text-ink">
        <p className="font-semibold">Query failed.</p>
        <p className="mt-1 text-black/70">{result.error}</p>
      </div>
    );
  }

  if (result.rows.length === 0) {
    return (
      <div className="rounded-md border border-black/10 bg-white p-4 text-sm text-black/70">
        No rows yet. Run the pipeline or seed fixtures to populate this view.
      </div>
    );
  }

  return null;
}
