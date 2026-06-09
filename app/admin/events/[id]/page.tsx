import { getMarketEventById } from "@/lib/admin-data";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function EventDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  const result = await getMarketEventById(resolvedParams.id);

  if (!result.configured) {
    return <div className="rounded-xl border border-red-500 bg-red-50 p-6 text-red-700">Database not configured. Missing: {result.missing?.join(", ")}</div>;
  }
  if (result.error) {
    return <div className="rounded-xl border border-red-500 bg-red-50 p-6 text-red-700">Error loading event: {result.error}</div>;
  }
  
  const event = result.row;
  if (!event) notFound();

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      <Link href="/admin/events" className="inline-flex items-center text-moss hover:text-moss/80 font-medium transition-colors">
        <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        Back to Global Radar
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <span className={`px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase ${
              event.event_type.includes('BLEEDING') ? 'bg-green-100 text-green-800' : 
              event.event_type.includes('ENCROACHMENT') ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {event.event_type.replace(/_/g, ' ')}
            </span>
            <span className="text-sm font-medium text-black/40">
              {new Date(event.detected_at).toLocaleString()}
            </span>
          </div>
          <h1 className="text-4xl font-black text-ink tracking-tight mt-4">Event Dossier</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
        <div className="space-y-6">
          <h3 className="text-xl font-bold border-b pb-2 text-ink">Metadata</h3>
          <div className="bg-white rounded-2xl border border-black/10 p-6 space-y-4 shadow-sm">
            <div className="flex justify-between border-b border-black/5 pb-3">
              <span className="text-black/50">Agency</span>
              <div className="text-right">
                <span className="font-bold block">{event.payload?.agency_name || event.target_agency_id || "N/A"}</span>
                {event.payload?.agency_name && <span className="text-xs text-black/40">{event.target_agency_id}</span>}
              </div>
            </div>
            {event.target_agent_npn && (
              <div className="flex justify-between border-b border-black/5 pb-3">
                <span className="text-black/50">Agent</span>
                <div className="text-right">
                  <span className="font-bold block">{event.payload?.agent_name || event.target_agent_npn}</span>
                  {event.payload?.agent_name && <span className="text-xs text-black/40">NPN: {event.target_agent_npn}</span>}
                </div>
              </div>
            )}
            <div className="flex justify-between border-b border-black/5 pb-3">
              <span className="text-black/50">Location</span>
              <span className="font-bold">{event.event_zip} {event.event_county ? `(${event.event_county})` : ''}</span>
            </div>
            {event.payload?.tenure_months && (
              <div className="flex justify-between border-b border-black/5 pb-3">
                <span className="text-black/50">Tenure</span>
                <span className="font-bold">{Math.floor(event.payload.tenure_months / 12)} Years, {event.payload.tenure_months % 12} Months</span>
              </div>
            )}
            <div className="flex justify-between"><span className="text-black/50">Confidence</span><span className="font-bold uppercase text-moss">{event.confidence}</span></div>
          </div>
        </div>

        <div className="space-y-6">
          <h3 className="text-xl font-bold border-b pb-2 text-ink">Raw Payload</h3>
          <div className="bg-slate-900 rounded-2xl p-6 shadow-xl overflow-x-auto h-[400px]">
            <pre className="text-green-400 font-mono text-sm">
              {JSON.stringify(event.payload, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
