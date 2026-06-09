import { getMarketAccessArbitrage } from "@/lib/admin-data";
import Link from "next/link";

export default async function ArbitrageHunterPage({ searchParams }: { searchParams: Promise<{ buyer_id?: string }> }) {
  const resolvedParams = await searchParams;
  const buyerId = resolvedParams.buyer_id || "";
  
  const result = buyerId ? await getMarketAccessArbitrage(buyerId) : { configured: true, rows: [] };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="bg-gradient-to-br from-moss/20 to-transparent p-8 rounded-2xl border border-moss/20 backdrop-blur-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-10 opacity-10 pointer-events-none">
          <svg width="200" height="200" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 22h20L12 2zm0 4.5l6.5 13h-13L12 6.5z" />
          </svg>
        </div>
        <p className="text-sm font-bold uppercase tracking-widest text-moss mb-2">Talent Acquisition</p>
        <h2 className="text-4xl font-black text-ink tracking-tight">Arbitrage Hunter</h2>
        <p className="text-black/60 mt-2 max-w-2xl text-lg">
          Cross-reference your agency's carrier appointments against local competitors to identify top producers who are trapped without your market access.
        </p>

        <form className="mt-8 flex items-center space-x-3 max-w-xl">
          <input 
            type="text" 
            name="buyer_id" 
            defaultValue={buyerId}
            placeholder="Enter Your Agency TDI ID (e.g. 12345)" 
            className="flex-1 rounded-xl border border-black/10 bg-white/80 px-4 py-3 text-ink shadow-sm focus:border-moss focus:ring-2 focus:ring-moss/20 outline-none transition-all"
            required
          />
          <button type="submit" className="bg-moss text-white px-6 py-3 rounded-xl font-semibold shadow-md hover:bg-moss/90 transition-colors hover:scale-105 active:scale-95 duration-200">
            Hunt Talent
          </button>
        </form>
      </div>

      {buyerId && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-ink">Targets Found: <span className="text-moss">{result.rows.length}</span></h3>
          
          {!result.configured && (
            <div className="rounded-xl border border-red-500 bg-red-50 p-4 text-red-700">
              Database not configured.
            </div>
          )}

          {result.rows.length === 0 && result.configured && (
            <div className="rounded-xl border border-black/5 bg-black/5 p-10 text-center text-black/50">
              No trapped talent found for this agency in their county. They either lack premium carriers or competitors have matched their capacity.
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.rows.map((target, idx) => (
              <div key={`${target.target_agent_npn}-${idx}`} className="group rounded-2xl border border-black/10 bg-white p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-bold text-ink">{target.agent_name}</h4>
                    <p className="text-sm text-black/50 font-mono">NPN: {target.target_agent_npn}</p>
                  </div>
                  <div className="bg-black/5 rounded-lg px-3 py-1 text-xs font-bold text-black/70">
                    {target.agent_total_carriers} Active Lines
                  </div>
                </div>
                
                <div className="mb-4">
                  <p className="text-xs font-semibold text-black/40 uppercase tracking-wider mb-1">Trapped At</p>
                  <p className="text-red-700 font-medium line-clamp-1">{target.competitor_agency_name}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-semibold text-black/40 uppercase tracking-wider">Lacking Carriers You Have</p>
                  <div className="flex flex-wrap gap-2">
                    {target.missing_buyer_carriers.map((carrier) => (
                      <span key={carrier.carrier_naic} className="px-3 py-1 bg-moss/10 text-moss border border-moss/20 rounded-full text-xs font-bold shadow-sm">
                        {carrier.carrier_name}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-black/5">
                  <button className="w-full py-2 bg-black text-white rounded-lg font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/80">
                    Generate Poaching Email
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
