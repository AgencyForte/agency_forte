import { getMarketEventById } from "@/lib/admin-data";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function EventDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  const result = await getMarketEventById(resolvedParams.id);

  if (!result.configured) {
    return (
      <div className="rounded-md border border-red-500 bg-red-50 p-4 text-red-700">
        Database not configured. Missing: {result.missing?.join(", ")}
      </div>
    );
  }

  if (result.error) {
    return (
      <div className="rounded-md border border-red-500 bg-red-50 p-4 text-red-700">
        Error loading event: {result.error}
      </div>
    );
  }

  const event = result.row;

  if (!event) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/admin/events" className="text-moss hover:underline">
          &larr; Back to Events
        </Link>
      </div>

      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-moss">Event Detail</p>
        <h2 className="text-3xl font-semibold text-ink">{event.event_type}</h2>
        <p className="text-sm text-black/60 mt-1">Detected at: {event.detected_at}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-md border border-black/10 bg-white p-5 space-y-4">
          <h3 className="font-semibold text-lg border-b pb-2">Context</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-black/60">Review Status</dt>
              <dd className="font-medium">{event.review_status}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-black/60">Target Agency ID</dt>
              <dd className="font-medium">{event.target_agency_id || "N/A"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-black/60">Target Agent NPN</dt>
              <dd className="font-medium">{event.target_agent_npn || "N/A"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-black/60">Carrier NAIC</dt>
              <dd className="font-medium">{event.carrier_naic || "N/A"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-black/60">ZIP / Location</dt>
              <dd className="font-medium">{event.event_zip || "N/A"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-black/60">Confidence</dt>
              <dd className="font-medium capitalize">{event.confidence || "N/A"}</dd>
            </div>
          </dl>
        </div>

        <div className="rounded-md border border-black/10 bg-white p-5 space-y-4">
          <h3 className="font-semibold text-lg border-b pb-2">Payload</h3>
          <div className="bg-field p-4 rounded text-sm overflow-x-auto">
            <pre className="text-ink">
              {JSON.stringify(event.payload, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
