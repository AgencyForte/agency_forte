import Link from "next/link";

const navItems = [
  { href: "/admin/pipeline-runs", label: "Pipeline Runs" },
  { href: "/admin/events", label: "Events" },
  { href: "/admin/suppressed-severances", label: "Suppressed Severances" },
  { href: "/admin/anomalies", label: "Anomalies" },
  { href: "/admin/arbitrage", label: "Arbitrage Hunter" }
];

export function AdminShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <main className="min-h-screen">
      <header className="border-b border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-moss">Insuretra</p>
            <h1 className="text-xl font-semibold text-ink">Pipeline Operations</h1>
          </div>
          <nav className="flex flex-wrap gap-2 text-sm">
            {navItems.map((item) => (
              <Link
                className="rounded-md border border-black/10 px-3 py-2 font-medium text-ink hover:border-moss hover:text-moss"
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <section className="mx-auto max-w-7xl px-6 py-8">{children}</section>
    </main>
  );
}
