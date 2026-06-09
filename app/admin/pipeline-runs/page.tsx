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
          { key: "started_at", label: "Started" },
          { key: "status", label: "Status" },
          { key: "row_delta", label: "Row Delta" },
          { key: "event_count", label: "Events" },
          { key: "suppressed_count", label: "Suppressed" },
          { key: "finished_at", label: "Finished" }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
