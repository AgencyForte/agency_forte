import { getMarketAccessArbitrage } from "@/lib/admin-data";
import { headers } from "next/headers";

export default async function RecruitPage({ searchParams }: { searchParams: Promise<{ tenant?: string }> }) {
  const resolvedParams = await searchParams;
  const tenantId = resolvedParams.tenant || "npn:123456";
  const result = await getMarketAccessArbitrage(tenantId);
  const headersList = await headers();
  const isPublic = headersList.get("x-is-public") === "true";

  const targets = result.configured ? result.rows : [];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
            Market Access Arbitrage
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-xl">
            Target high-performing veteran producers whose current employers lack the exclusive carrier appointments you hold. Leverage your market access to recruit top talent.
          </p>
        </div>
        
        {/* Venn Diagram Visual Split Graph */}
        <div className="bg-[#1A1D26] px-6 py-4 rounded-2xl border border-white/5 shadow-lg flex items-center gap-4">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full border-2 border-blue-500/50 flex items-center justify-center bg-blue-500/10">
              <span className="text-blue-500 font-bold text-sm">YOU</span>
            </div>
          </div>
          <div className="text-slate-500 font-black text-xl">-</div>
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full border-2 border-slate-500/50 flex items-center justify-center bg-slate-500/10">
              <span className="text-slate-500 font-bold text-sm">THEM</span>
            </div>
          </div>
          <div className="text-slate-500 font-black text-xl">=</div>
          <div className="flex flex-col items-center">
            <div className="text-2xl font-black text-white">{targets.length}</div>
            <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mt-1">Targets</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {targets.length === 0 ? (
          <div className="col-span-full py-16 text-center rounded-3xl border border-dashed border-white/10 bg-[#1A1D26]/50">
            <p className="text-slate-500">No arbitrage targets currently mapped against your carrier portfolio.</p>
          </div>
        ) : targets.map((target, idx) => (
          <div key={idx} className="bg-[#1A1D26] rounded-3xl border border-white/5 shadow-xl p-6 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500"></div>
            
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className={`text-xl font-bold text-white tracking-tight ${isPublic ? 'blur-sm opacity-50' : ''}`}>
                  {isPublic ? '██████████' : target.agent_name}
                </h3>
                <div className="text-xs text-slate-500 font-mono mt-1">
                  NPN: {isPublic ? <span className="blur-sm">██████</span> : target.target_agent_npn}
                </div>
              </div>
              <div className="px-2 py-1 rounded bg-[#12141C] border border-white/5 text-[10px] uppercase tracking-widest text-slate-400 font-bold font-mono">
                52 Months Active
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">Current Roof</p>
                <p className={`text-sm text-slate-300 font-medium ${isPublic ? 'blur-sm opacity-50' : ''}`}>
                  {isPublic ? '████████████████' : target.competitor_agency_name}
                </p>
              </div>

              <div className="bg-[#12141C] p-3 rounded-xl border border-white/5 relative">
                <p className="text-[10px] uppercase tracking-widest text-blue-400 font-bold mb-2 flex items-center gap-1.5">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Leverage Logic
                </p>
                <p className="text-xs text-slate-400 leading-relaxed">
                  This producer is entirely locked out of <strong className="text-white">{(target.missing_buyer_carriers || []).map(c => c.carrier_name).join(", ")}</strong>. You hold these active appointments.
                </p>
              </div>
            </div>

            {isPublic ? (
              <button className="w-full py-3 bg-white/5 hover:bg-white/10 text-white font-black text-xs uppercase tracking-widest rounded-xl transition-colors border border-white/10 flex items-center justify-center gap-2">
                <svg className="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                Reveal Identity
              </button>
            ) : (
              <div className="space-y-2">
                <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-black text-xs uppercase tracking-widest rounded-xl transition-colors shadow-lg shadow-blue-500/20">
                  Initiate Outreach Pipeline
                </button>
                <button className="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white font-bold text-xs rounded-xl transition-colors">
                  Purchase Enriched Lead Pack ($49)
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
