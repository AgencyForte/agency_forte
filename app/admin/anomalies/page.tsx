import { DataState } from "@/components/data-state";
import { OpsTable } from "@/components/table";
import { getPipelineAnomalies } from "@/lib/admin-data";

export default async function AnomaliesPage() {
  const result = await getPipelineAnomalies();
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-moss">Operations</p>
        <h2 className="text-3xl font-semibold text-ink">Anomalies</h2>
      </div>
      <DataState result={result} />
      <OpsTable
        columns={[
          { key: "detected_at", label: "Detected" },
          { key: "severity", label: "Severity" },
          { key: "anomaly_type", label: "Type" },
          { key: "message", label: "Message" }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
