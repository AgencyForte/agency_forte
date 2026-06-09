"use client";

import { useWarRoom } from "@/components/war-room-context";

export default function MapPage() {
  const { activeTenant, isPublicParanoia } = useWarRoom();

  return (
    <div className="h-full flex flex-col space-y-4 animate-in fade-in duration-700">
      <div className="flex justify-between items-end shrink-0">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>
            Spatial Visualization
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-xl">
            Live geographical bounding data (`texas_zip_geo`) mapping active asymmetric threats against your agency's subscription radius.
          </p>
        </div>
      </div>

      <div className="flex-1 min-h-[500px] relative rounded-3xl border border-white/10 bg-[#0A0C10] overflow-hidden shadow-2xl flex items-center justify-center">
        {/* Synthetic Map Grid Background */}
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: `linear-gradient(#1A1D26 1px, transparent 1px), linear-gradient(90deg, #1A1D26 1px, transparent 1px)`, backgroundSize: '40px 40px' }}></div>
        
        {/* Paid Subscription Blast Radius (Translucent Boundary) */}
        <div className="absolute w-[400px] h-[400px] rounded-full bg-blue-500/5 border border-blue-500/20 shadow-[0_0_100px_rgba(59,130,246,0.1)] flex items-center justify-center pointer-events-none">
          <div className="absolute top-4 left-1/2 -translate-x-1/2 text-[10px] font-bold uppercase tracking-widest text-blue-500/50">
            {activeTenant.radius} Boundary
          </div>
        </div>

        {/* Tenant Central Hub */}
        <div className="absolute z-20 flex flex-col items-center justify-center group cursor-pointer">
          <div className="absolute w-24 h-24 rounded-full bg-blue-500/20 animate-ping opacity-50"></div>
          <div className="w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-[0_0_15px_rgba(37,99,235,0.8)] z-10"></div>
          <div className="mt-3 bg-[#12141C] border border-blue-500/30 px-3 py-1.5 rounded shadow-lg text-center opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-xs font-bold text-white whitespace-nowrap">{isPublicParanoia ? '████████' : activeTenant.name}</p>
            <p className="text-[10px] text-blue-400 font-mono">Hub: {isPublicParanoia ? '█████' : activeTenant.zip}</p>
          </div>
        </div>

        {/* Rival 1: Offense (Amber) */}
        <div className="absolute z-10 flex flex-col items-center justify-center group cursor-pointer" style={{ top: '30%', left: '35%' }}>
          <div className="w-4 h-4 bg-amber-500 rounded-full shadow-[0_0_10px_rgba(245,158,11,0.8)] z-10"></div>
          <div className="mt-2 bg-[#1A1D26] border border-amber-500/30 px-2 py-1 rounded shadow-lg text-center opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-[10px] font-bold text-amber-500 uppercase">Bleeding Event</p>
          </div>
        </div>

        {/* Rival 2: Defense (Red) */}
        <div className="absolute z-10 flex flex-col items-center justify-center group cursor-pointer" style={{ top: '65%', right: '40%' }}>
          <div className="w-4 h-4 bg-red-500 rounded-full shadow-[0_0_10px_rgba(239,68,68,0.8)] z-10"></div>
          <div className="mt-2 bg-[#1A1D26] border border-red-500/30 px-2 py-1 rounded shadow-lg text-center opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-[10px] font-bold text-red-500 uppercase">Encroachment</p>
          </div>
        </div>

        {/* Rival 3: Safe (Slate) */}
        <div className="absolute z-10 flex flex-col items-center justify-center group cursor-pointer" style={{ top: '20%', right: '25%' }}>
          <div className="w-3 h-3 bg-slate-600 rounded-full z-10"></div>
        </div>
      </div>
    </div>
  );
}
