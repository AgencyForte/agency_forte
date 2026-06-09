import { DataState } from "@/components/data-state";
import { OpsTable } from "@/components/table";
import { getSuppressedSeverances } from "@/lib/admin-data";

export default async function SuppressedSeverancesPage() {
  const result = await getSuppressedSeverances();
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-moss">HITL</p>
        <h2 className="text-3xl font-semibold text-ink">Suppressed Severances</h2>
      </div>
      <DataState result={result} />
      <OpsTable
        columns={[
          { key: "detected_at", label: "Detected" },
          { key: "agent_npn", label: "Agent NPN" },
          { key: "agency_tdi_id", label: "Agency" },
          { key: "relationship_started_at", label: "Started" },
          { key: "relationship_ended_at", label: "Ended" },
          { key: "tenure_months", label: "Months" },
          { key: "suppression_reason", label: "Reason" }
        ]}
        rows={result.rows}
      />
    </div>
  );
}
