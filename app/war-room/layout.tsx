import { headers } from "next/headers";
import Link from "next/link";
import { WarRoomProvider } from "@/components/war-room-context";
import { TenantHeaderSwitcher } from "@/components/tenant-header-switcher";
import { ParanoiaModal } from "@/components/paranoia-modal";

export default async function WarRoomLayout({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const isPublicParanoia = headersList.get("x-is-public") === "true";
  
  // Default to Austin Premier for SSR
  const defaultTenantId = "npn:123456";

  return (
    <WarRoomProvider initialTenantId={defaultTenantId} isPublicParanoia={isPublicParanoia}>
      <div className="min-h-screen bg-[#0F1115] text-slate-300 font-sans selection:bg-amber-500/30">
        
        {/* Global Navigation & Persistent Buyer Profile Anchor */}
        <header className="sticky top-0 z-40 bg-[#12141C] border-b border-white/5 shadow-2xl">
          <div className="flex flex-col lg:flex-row justify-between items-center px-6 py-4 gap-4">
            
            {/* Left Panel: Brand & Market Hub */}
            <div className="flex items-center gap-6">
              <div className="flex flex-col">
                <h1 className="text-xl font-bold tracking-tight text-white uppercase flex items-center gap-2">
                  <svg className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                  AgencyForte
                </h1>
                <span className="text-[10px] text-amber-500/80 font-bold tracking-[0.2em] uppercase mt-0.5 ml-7">War Room</span>
              </div>
              <div className="h-8 w-px bg-white/10 hidden lg:block"></div>
              <TenantHeaderSwitcher />
            </div>

            {/* Right Panel: Buyer Asset Capsule */}
            <BuyerAssetCapsule />
          </div>
        </header>

        {/* Workspace Layout */}
        <div className="flex flex-col lg:flex-row h-[calc(100vh-80px)]">
          {/* Fixed Left Sidebar */}
          <aside className="lg:w-64 bg-[#12141C] border-r border-white/5 flex flex-col p-4 shrink-0 overflow-y-auto">
            <nav className="space-y-1.5 flex-1">
              <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4 mt-2">Tactical Command</p>
              <SidebarLink href="/war-room/map" label="Spatial Map" icon="map" />
              <SidebarLink href="/war-room/offense" label="Offense (Bleeding)" icon="target" highlight="amber" />
              <SidebarLink href="/war-room/recruit" label="Recruit (Arbitrage)" icon="users" />
              <SidebarLink href="/war-room/defense" label="Defense (Encroachment)" icon="shield" highlight="emerald" />
            </nav>
            <div className="mt-auto pt-6 border-t border-white/5">
              <div className="bg-[#1A1D26] p-4 rounded-xl border border-white/5 shadow-inner">
                <div className="flex items-center gap-2 text-emerald-400 mb-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                  <span className="text-[10px] font-bold uppercase tracking-wider">Engine Active</span>
                </div>
                <p className="text-xs text-slate-500">Global ingest sync complete. Filtering via Buyer Lens.</p>
              </div>
            </div>
          </aside>

          {/* Central Frame */}
          <main className="flex-1 relative overflow-hidden bg-[#0F1115]">
            <div className="h-full overflow-y-auto p-6 lg:p-10 relative scroll-smooth">
              {children}
            </div>
          </main>
        </div>

        {/* V2 pSEO Modal */}
        {isPublicParanoia && <ParanoiaModal />}
      </div>
    </WarRoomProvider>
  );
}

import { useWarRoom } from "@/components/war-room-context";

function BuyerAssetCapsule() {
  const { activeTenant } = useWarRoom();
  return (
    <div className="flex items-center gap-6 bg-[#1A1D26] px-5 py-2.5 rounded-2xl border border-white/5 shadow-inner hidden md:flex">
      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-0.5">Monitored Radius</span>
        <span className="text-xs text-emerald-400 font-medium flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          {activeTenant.radius}
        </span>
      </div>
      <div className="w-px h-6 bg-white/10"></div>
      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-0.5">Carrier Footprint</span>
        <span className="text-xs text-white font-medium flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
          {activeTenant.appointments} Standard Active
        </span>
      </div>
      <div className="w-px h-6 bg-white/10"></div>
      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-0.5">Monitored Lines</span>
        <span className="text-xs text-white font-medium truncate max-w-[200px]">
          {activeTenant.monitoredLines.join(", ")}
        </span>
      </div>
    </div>
  );
}

function SidebarLink({ href, label, icon, highlight }: { href: string; label: string; icon: string; highlight?: 'amber' | 'emerald' }) {
  // In a real app we'd use usePathname to highlight active route
  return (
    <Link href={href} className="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors">
      {icon === 'map' && <svg className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>}
      {icon === 'target' && <svg className={`w-4 h-4 ${highlight === 'amber' ? 'text-amber-500' : 'text-slate-500'} group-hover:text-amber-400 transition-colors`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
      {icon === 'users' && <svg className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>}
      {icon === 'shield' && <svg className={`w-4 h-4 ${highlight === 'emerald' ? 'text-emerald-500' : 'text-slate-500'} group-hover:text-emerald-400 transition-colors`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>}
      {label}
    </Link>
  );
}
