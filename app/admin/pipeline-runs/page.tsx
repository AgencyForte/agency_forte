import { DataState } from "@/components/data-state";
import { OpsTable } from "@/components/table";
import { getPipelineRuns } from "@/lib/admin-data";

export default async function PipelineRunsPage() {
  const result = await getPipelineRuns();
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-moss">Admin</p>
        <h2 className="text-3xl font-semibold text-ink">Pipeline Runs</h2>
      </div>
      <DataState result={result} />
      <OpsTable
        columns={[
          { 
            key: "started_at", 
            label: "Started",
            render: (row) => new Date(row.started_at).toLocaleString(undefined, {
              month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
            })
          },
          { 
            key: "status", 
            label: "Status",
            render: (row) => (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize ${
                row.status === 'succeeded' ? 'bg-green-100 text-green-800 border border-green-200' :
                row.status === 'failed' ? 'bg-red-100 text-red-800 border border-red-200' :
                'bg-yellow-100 text-yellow-800 border border-yellow-200'
              }`}>
                {row.status}
              </span>
            )
          },
          { 
            key: "row_delta", 
            label: "Row Delta",
            render: (row) => row.row_delta?.toLocaleString() || "-"
          },
          { key: "event_count", label: "Events" },
          { key: "suppressed_count", label: "Suppressed" },
          { 
            key: "finished_at", 
            label: "Finished",
            render: (row) => row.finished_at ? new Date(row.finished_at).toLocaleString(undefined, {
              month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
            }) : "-"
          }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
