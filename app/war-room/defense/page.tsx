import { getBuyerAlerts } from "@/lib/admin-data";
import { headers } from "next/headers";

export default async function DefensePage({ searchParams }: { searchParams: Promise<{ tenant?: string }> }) {
  const resolvedParams = await searchParams;
  const tenantId = resolvedParams.tenant || "npn:123456";
  const result = await getBuyerAlerts(tenantId);
  const headersList = await headers();
  const isPublic = headersList.get("x-is-public") === "true";

  // Strictly filter for Encroachment
  const events = result.configured ? result.rows.filter(e => e.event_type === "LOB_ENCROACHMENT") : [];

  return (
    <div className="space-y-8 animate-in fade-in duration-700 max-w-5xl">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <svg className="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            Encroachment Shield
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-xl">
            Protect your book of business. This radar only alerts you when a local rival secures a veteran hire or appointment that directly overlaps with your specific product lines.
          </p>
        </div>
        
        {/* Permanent Status Badge */}
        <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-xl flex items-center gap-3 shadow-lg shadow-emerald-500/5">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </div>
          <p className="text-xs font-bold text-emerald-500 tracking-wide uppercase">
            Noise-Filter Activated: Suppressing non-overlapping local movements
          </p>
        </div>
      </div>

      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
        {events.length === 0 ? (
          <div className="relative z-10 py-16 text-center rounded-3xl border border-dashed border-white/10 bg-[#1A1D26]/80 backdrop-blur-sm max-w-2xl mx-auto">
            <svg className="w-12 h-12 text-emerald-500/30 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            <p className="text-emerald-400 font-bold">Shield Intact</p>
            <p className="text-slate-500 text-sm mt-1">No local competitors have breached your active product lines recently.</p>
          </div>
        ) : events.map(event => {
          const payload = event.payload || {};
          return (
            <div key={event.event_id} className="relative z-10">
              <div className="md:flex items-center justify-between">
                <div className="hidden md:block w-[calc(50%-2rem)] text-right pr-8">
                  <span className="text-xs font-bold text-slate-500 font-mono">
                    {new Date(event.detected_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
                
                <div className="absolute left-0 md:left-1/2 -translate-x-1/2 flex items-center justify-center w-10 h-10 rounded-full bg-[#12141C] border-2 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                  <svg className="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                </div>
                
                <div className="ml-14 md:ml-0 md:w-[calc(50%-2rem)] pl-0 md:pl-8">
                  <div className="bg-[#1A1D26] p-6 rounded-2xl border border-red-500/20 shadow-xl relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-orange-500"></div>
                    
                    <div className="mb-4">
                      <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-red-500/10 text-red-500 border border-red-500/20 mb-3">
                        [CRITICAL ALERT: COMPETITOR CAPACITY EXPANSION]
                      </span>
                      <h3 className={`text-xl font-bold text-white tracking-tight ${isPublic ? 'blur-sm opacity-50' : ''}`}>
                        {isPublic ? '████████████' : (payload.agency_name || event.target_agency_id)}
                      </h3>
                      <p className="text-sm text-slate-400 mt-1 font-medium">
                        {payload.source_rule === 'veteran_hire_overlap' ? 'Hired overlapping veteran producer' : 'Secured overlapping carrier appointment'} 
                        {' '}in <span className={`text-white font-mono ${isPublic ? 'blur-sm' : ''}`}>{isPublic ? '█████' : event.event_zip}</span>
                      </p>
                    </div>

                    <div className="bg-[#12141C] p-3 rounded-xl border border-white/5">
                      <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Specific LOB Overlap</p>
                      <div className="flex gap-2 flex-wrap">
                        {(payload.lines_overlapped || []).map((line: string) => (
                          <span key={line} className="px-2 py-1 rounded text-xs font-bold text-red-400 bg-red-500/10 border border-red-500/20">
                            {line}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-white/5">
                      <p className="text-[10px] uppercase tracking-widest text-amber-500 font-bold mb-1 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                        Tactical Playbook
                      </p>
                      <p className="text-xs text-slate-400">
                        Deploy immediate defensive retention sequences to your <strong className="text-white">{(payload.lines_overlapped || [])[0]}</strong> renewals in {isPublic ? '█████' : event.event_zip}. This rival has directly expanded capacity to target your book.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
