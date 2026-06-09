import { DataState } from "@/components/data-state";
import { OpsTable } from "@/components/table";
import { getMarketEvents } from "@/lib/admin-data";
import Link from "next/link";

export default async function EventsPage() {
  const result = await getMarketEvents();
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-moss">Timeline</p>
        <h2 className="text-3xl font-semibold text-ink">Market Events</h2>
      </div>
      <DataState result={result} />
      <OpsTable
        columns={[
          { key: "detected_at", label: "Detected" },
          { 
            key: "event_type", 
            label: "Type",
            render: (row) => (
              <Link href={`/admin/events/${row.event_id}`} className="text-blue-600 hover:underline">
                {row.event_type}
              </Link>
            )
          },
          { key: "review_status", label: "Review" },
          { key: "target_agency_id", label: "Agency" },
          { key: "target_agent_npn", label: "Agent" },
          { key: "carrier_naic", label: "Carrier" },
          { key: "event_zip", label: "ZIP" },
          { key: "confidence", label: "Confidence" }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
