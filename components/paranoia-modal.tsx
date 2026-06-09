"use client";

import Link from "next/link";

export function ParanoiaModal() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0F1115]/80 backdrop-blur-md">
      <div className="bg-[#1A1D26] border border-amber-500/50 rounded-2xl shadow-2xl shadow-amber-500/10 p-8 max-w-lg w-full text-center mx-4">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-500 rounded-full flex items-center justify-center mx-auto mb-6 ring-4 ring-amber-500/5">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Intelligence Encrypted</h2>
        <p className="text-slate-400 mb-8 font-medium">
          Your competitors are currently viewing your agency's data. Subscribe to claim your territory and unmask local asymmetrical threats.
        </p>
        <Link 
          href="/pricing"
          className="block w-full py-4 px-6 bg-amber-500 hover:bg-amber-400 text-[#0F1115] font-black text-sm uppercase tracking-widest rounded-xl transition-colors shadow-lg shadow-amber-500/20"
        >
          Claim Your Territory
        </Link>
        <p className="mt-4 text-[10px] uppercase tracking-wider text-slate-500 font-bold">
          Programmatic SEO Paywall V2
        </p>
      </div>
    </div>
  );
}
