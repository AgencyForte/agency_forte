"use client";

import { useWarRoom, TENANTS } from "./war-room-context";
import { useRouter, usePathname, useSearchParams } from "next/navigation";

export function TenantHeaderSwitcher() {
  const { activeTenant, setActiveTenant, isPublicParanoia } = useWarRoom();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  if (isPublicParanoia) {
    return (
      <div className="flex items-center gap-2 text-white">
        <span className="text-sm font-semibold opacity-30 blur-sm">███████████</span>
        <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
      </div>
    );
  }

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newId = e.target.value;
    setActiveTenant(newId);
    
    // Update URL to trigger SSR data refetching
    const params = new URLSearchParams(searchParams.toString());
    params.set('tenant', newId);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <select
      value={activeTenant.id}
      onChange={handleChange}
      className="bg-[#1A1D26] border border-white/10 text-white text-sm rounded-lg focus:ring-amber-500 focus:border-amber-500 block w-full p-2.5 font-medium shadow-sm outline-none appearance-none pr-8 relative cursor-pointer"
      style={{ backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.5rem center', backgroundSize: '1em' }}
    >
      {TENANTS.map(t => (
        <option key={t.id} value={t.id}>{t.name}</option>
      ))}
    </select>
  );
}
