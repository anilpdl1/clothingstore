import { useEffect, useState } from "react";
import api from "../services/api";
export default function AdminReviews() {
  const [reviews, setReviews] = useState([]);
  const load = () => api.get("/admin/reviews").then((r) => setReviews(r.data));
  useEffect(() => {
    void load();
  }, []);
  const action = async (id, kind) => {
    if (kind === "delete") await api.delete(`/admin/reviews/${id}`);
    else await api.put(`/admin/reviews/${id}/${kind}`);
    load();
  };
  return (
    <section className="mx-auto max-w-7xl px-5 py-10">
      <h1 className="text-4xl font-bold">Review moderation</h1>
      <p className="mt-2 text-stone-600">
        Approve, reject, or remove customer feedback. Report counts indicate
        content requiring attention.
      </p>
      <div className="mt-8 space-y-4">
        {reviews.map((r) => (
          <article className="rounded-xl border p-5" key={r.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-bold">
                  {r.product} · ★ {r.rating}
                </p>
                <p className="text-sm text-stone-500">
                  {r.user} · {new Date(r.created_at).toLocaleDateString()} ·{" "}
                  {r.verified_purchase ? "Verified purchase" : "Unverified"}
                </p>
                <h2 className="mt-3 font-semibold">{r.title}</h2>
                <p>{r.comment}</p>
              </div>
              <div className="flex gap-2">
                <span className="rounded-full bg-stone-100 px-3 py-1 text-sm">
                  {r.status}
                </span>
                {r.reports > 0 && (
                  <span className="rounded-full bg-red-100 px-3 py-1 text-sm">
                    {r.reports} reports
                  </span>
                )}
              </div>
            </div>
            <div className="mt-4 flex gap-3">
              <button
                className="rounded-full border px-3 py-1"
                onClick={() => action(r.id, "approve")}
              >
                Approve
              </button>
              <button
                className="rounded-full border px-3 py-1"
                onClick={() => action(r.id, "reject")}
              >
                Reject
              </button>
              <button
                className="rounded-full border px-3 py-1 text-red-700"
                onClick={() => action(r.id, "delete")}
              >
                Delete
              </button>
            </div>
          </article>
        ))}
        {!reviews.length && (
          <p className="text-stone-500">No reviews to moderate.</p>
        )}
      </div>
    </section>
  );
}
