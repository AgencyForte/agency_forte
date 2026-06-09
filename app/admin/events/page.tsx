import { getBuyerAlerts } from "@/lib/admin-data";
import Link from "next/link";

const TENANTS = [
  { id: "npn:123456", name: "Austin Premier Insurance Group", zip: "78701", county: "Travis" },
  { id: "npn:654321", name: "Dallas Elite Risk Partners", zip: "75201", county: "Dallas" }
];

export default async function EventsPage({ searchParams }: { searchParams: Promise<{ tenant?: string }> }) {
  const resolvedParams = await searchParams;
  const currentTenantId = resolvedParams.tenant || "npn:123456";
  const currentTenant = TENANTS.find(t => t.id === currentTenantId) || TENANTS[0];
  
  const result = await getBuyerAlerts(currentTenantId);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-700 mt-8 mb-20">
      {/* Header & Tenant Switcher */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-black/5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-moss mb-2 flex items-center">
            <span className="w-2 h-2 rounded-full bg-moss mr-2 animate-pulse"></span>
            Intelligence Radar
          </p>
          <h2 className="text-4xl font-black text-ink tracking-tight">Active Threats</h2>
          <p className="text-black/50 mt-2 text-sm max-w-lg">
            Adversarial shifts mapped against your agency's product lines and geographic territories. Non-intersecting noise is automatically suppressed.
          </p>
        </div>

        <div className="bg-slate-50 p-2 rounded-2xl border border-black/5 shadow-sm">
          <p className="text-[10px] font-bold uppercase tracking-wider text-black/40 px-3 pt-1 mb-1">Simulated Tenant Profile</p>
          <div className="flex gap-2">
            {TENANTS.map((tenant) => (
              <Link 
                key={tenant.id} 
                href={`/admin/events?tenant=${tenant.id}`}
                className={`px-4 py-2 text-sm font-medium rounded-xl transition-all duration-300 ${
                  currentTenantId === tenant.id 
                    ? 'bg-white text-ink shadow-sm ring-1 ring-black/5 scale-100' 
                    : 'text-black/40 hover:text-black/80 hover:bg-black/5 scale-95'
                }`}
              >
                {tenant.name}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Database Error State */}
      {!result.configured && (
        <div className="rounded-2xl border border-red-500/20 bg-red-50 p-8 text-red-700 shadow-sm">
          Database not configured. Missing: {result.missing?.join(", ")}
        </div>
      )}

      {/* Threat Cards Grid */}
      <div className="grid grid-cols-1 gap-6">
        {result.configured && result.rows.length === 0 ? (
          <div className="py-20 text-center flex flex-col items-center justify-center rounded-3xl border border-dashed border-black/10 bg-slate-50/50">
            <div className="w-16 h-16 rounded-full bg-white shadow-sm flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-black/20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h3 className="text-lg font-bold text-ink">Zero Threats Detected</h3>
            <p className="text-black/50 text-sm max-w-sm mt-1">No competitor shifts currently overlap with {currentTenant.name}'s product lines or radius.</p>
          </div>
        ) : (
          result.rows.map((event) => {
            const isBleeding = event.event_type.includes("BLEEDING");
            const isEncroachment = event.event_type.includes("ENCROACHMENT");
            const payload = event.payload || {};

            return (
              <div 
                key={event.event_id} 
                className="group relative bg-white rounded-3xl border border-black/5 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-500 overflow-hidden"
              >
                {/* Threat Indicator Accent */}
                <div className={`absolute top-0 left-0 w-1.5 h-full ${isBleeding ? 'bg-red-500' : isEncroachment ? 'bg-amber-500' : 'bg-blue-500'}`} />
                
                <div className="p-6 sm:p-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6 pl-10">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 text-[11px] font-black tracking-widest uppercase rounded-full ${
                        isBleeding ? 'bg-red-50 text-red-700 ring-1 ring-red-500/20' : 
                        isEncroachment ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-500/20' : 
                        'bg-blue-50 text-blue-700 ring-1 ring-blue-500/20'
                      }`}>
                        {event.event_type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs font-medium text-black/40">
                        Detected: {new Date(event.detected_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                    
                    <div>
                      <h3 className="text-2xl font-bold text-ink tracking-tight group-hover:text-blue-600 transition-colors">
                        {payload.agent_name ? `${payload.agent_name} at ${payload.agency_name || event.target_agency_id}` : (payload.agency_name || event.target_agency_id)}
                      </h3>
                      {payload.source_rule === 'veteran_hire_overlap' && (
                        <p className="text-sm text-black/60 mt-1 font-medium">Veteran producer hired into competing agency inside {event.event_zip}.</p>
                      )}
                      {payload.source_rule === '36_month_tenure_filter' && (
                        <p className="text-sm text-black/60 mt-1 font-medium">Top producer departed competing agency inside {event.event_zip}.</p>
                      )}
                    </div>
                  </div>

                  {/* Core Intelligence Vectors */}
                  <div className="flex flex-col sm:items-end gap-2 shrink-0">
                    {payload.tenure_months && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-black/40 font-medium">Tenure Impact:</span>
                        <span className="font-bold text-ink bg-slate-100 px-2 py-0.5 rounded-md">
                          {Math.floor(payload.tenure_months / 12)} Yrs, {payload.tenure_months % 12} Mos
                        </span>
                      </div>
                    )}
                    {payload.lines_overlapped && (
                      <div className="flex items-center gap-2 text-sm mt-1">
                        <span className="text-black/40 font-medium">Vectors:</span>
                        <div className="flex gap-1">
                          {(payload.lines_overlapped as string[]).slice(0, 2).map(line => (
                            <span key={line} className="font-bold text-[10px] uppercase tracking-wider text-amber-800 bg-amber-100 px-2 py-0.5 rounded-md">
                              {line}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    <Link 
                      href={`/admin/events/${event.event_id}`} 
                      className="mt-3 inline-flex items-center justify-center px-5 py-2.5 text-sm font-bold text-white bg-slate-900 rounded-xl hover:bg-slate-800 transition-colors shadow-md"
                    >
                      View Full Dossier
                      <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                    </Link>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
