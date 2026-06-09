import { getBuyerAlerts } from "@/lib/admin-data";
import Link from "next/link";
import { headers } from "next/headers";

export default async function OffensePage({ searchParams }: { searchParams: Promise<{ tenant?: string }> }) {
  const resolvedParams = await searchParams;
  const tenantId = resolvedParams.tenant || "npn:123456";
  const result = await getBuyerAlerts(tenantId);
  const headersList = await headers();
  const isPublic = headersList.get("x-is-public") === "true";

  // Filter strictly for COMPETITOR_BLEEDING
  const events = result.configured ? result.rows.filter(e => e.event_type === "COMPETITOR_BLEEDING") : [];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <svg className="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            Competitor Bleeding
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-xl">
            Active structural vulnerabilities at competing agencies within your monitored radius. Deploy direct mail or intercept accounts immediately.
          </p>
        </div>
        
        {/* Top Summary Cards */}
        <div className="flex gap-4">
          <div className="bg-[#1A1D26] px-6 py-4 rounded-2xl border border-white/5 shadow-lg flex flex-col items-end">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Active Vacancies</span>
            <span className="text-3xl font-black text-amber-500">{events.length}</span>
          </div>
          <div className="bg-[#1A1D26] px-6 py-4 rounded-2xl border border-white/5 shadow-lg flex flex-col items-end">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Orphaned ZIPs</span>
            <span className="text-3xl font-black text-white">{new Set(events.map(e => e.event_zip)).size}</span>
          </div>
        </div>
      </div>

      <div className="bg-[#1A1D26] rounded-2xl border border-white/5 shadow-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-[#12141C] text-[10px] uppercase tracking-widest text-slate-500 font-bold border-b border-white/5">
            <tr>
              <th className="px-6 py-4">Competitor Target</th>
              <th className="px-6 py-4">Trigger Event</th>
              <th className="px-6 py-4">Affected Lines</th>
              <th className="px-6 py-4 text-right">Playbook Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {events.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                  No active bleeding events within your monitored radius.
                </td>
              </tr>
            ) : events.map(event => {
              const payload = event.payload || {};
              const isCarrierPullout = event.target_agent_npn === null;
              
              return (
                <tr key={event.event_id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="font-bold text-white mb-1">
                      {isPublic ? <span className="blur-sm opacity-50">████████████</span> : (payload.agency_name || event.target_agency_id)}
                    </div>
                    <div className="text-xs text-slate-500 font-mono flex items-center gap-1.5">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                      ZIP: {isPublic ? <span className="blur-sm">█████</span> : event.event_zip}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-amber-500/10 text-amber-500 border border-amber-500/20">
                      {isCarrierPullout ? 'Carrier Appointment Pull-out' : `Veteran Producer Exit (${Math.floor(payload.tenure_months/12)} Yrs)`}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1.5 flex-wrap">
                      {(payload.historical_carriers || []).map((hc: any, i: number) => (
                        <span key={i} className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-[#12141C] border border-white/5 text-slate-400">
                          {hc.line_of_business}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-[#0F1115] font-black text-xs uppercase tracking-widest rounded-lg transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 shadow-lg shadow-amber-500/20">
                      {isCarrierPullout ? 'Deploy Direct Mail' : 'Intercept Accounts'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
