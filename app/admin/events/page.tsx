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
          { 
            key: "detected_at", 
            label: "Detected",
            render: (row) => new Date(row.detected_at).toLocaleString(undefined, {
              month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
            })
          },
          { 
            key: "event_type", 
            label: "Type",
            render: (row) => (
              <Link href={`/admin/events/${row.event_id}`} className="text-blue-600 hover:underline font-medium capitalize">
                {row.event_type.replace(/_/g, ' ').toLowerCase()}
              </Link>
            )
          },
          { 
            key: "review_status", 
            label: "Review",
            render: (row) => (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize whitespace-nowrap ${
                row.review_status === 'approved' ? 'bg-green-100 text-green-800 border border-green-200' :
                row.review_status === 'rejected' ? 'bg-red-100 text-red-800 border border-red-200' :
                'bg-yellow-100 text-yellow-800 border border-yellow-200'
              }`}>
                {row.review_status.replace(/_/g, ' ')}
              </span>
            )
          },
          { key: "target_agency_id", label: "Agency", render: (row) => row.target_agency_id || <span className="text-black/30">-</span> },
          { key: "target_agent_npn", label: "Agent", render: (row) => row.target_agent_npn || <span className="text-black/30">-</span> },
          { key: "carrier_naic", label: "Carrier", render: (row) => row.carrier_name || row.carrier_naic || <span className="text-black/30">-</span> },
          { key: "event_zip", label: "ZIP", render: (row) => row.event_zip || <span className="text-black/30">-</span> },
          { key: "event_county", label: "County", render: (row) => row.event_county || <span className="text-black/30">-</span> },
          {
            key: "is_processed",
            label: "Routing",
            render: (row) => (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${row.is_processed ? "bg-green-100 text-green-800 border border-green-200" : "bg-yellow-100 text-yellow-800 border border-yellow-200"}`}>
                {row.is_processed ? "Processed" : "Pending"}
              </span>
            )
          },
          { key: "confidence", label: "Confidence" }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
