import { login } from "./actions";

export default async function AdminLogin({
  searchParams
}: Readonly<{
  searchParams: Promise<{ error?: string; next?: string }>;
}>) {
  const params = await searchParams;
  const next = params.next ?? "/admin/pipeline-runs";

  return (
    <main className="flex min-h-screen items-center justify-center bg-field px-6">
      <form action={login} className="w-full max-w-sm rounded-md border border-black/10 bg-white p-6 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-moss">Insuretra</p>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Admin Access</h1>
        <input name="next" type="hidden" value={next} />
        <label className="mt-6 block text-sm font-medium text-ink" htmlFor="password">
          Admin password
        </label>
        <input
          className="mt-2 w-full rounded-md border border-black/15 px-3 py-2 text-ink outline-none focus:border-moss"
          id="password"
          name="password"
          type="password"
        />
        {params.error ? <p className="mt-3 text-sm text-signal">Invalid password.</p> : null}
        <button className="mt-6 w-full rounded-md bg-ink px-4 py-2 font-semibold text-white" type="submit">
          Sign in
        </button>
      </form>
    </main>
  );
}
