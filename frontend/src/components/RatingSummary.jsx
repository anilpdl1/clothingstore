import RatingStars from "./RatingStars";
export default function RatingSummary({ summary }) {
  const total = summary?.total_reviews || 0;
  return (
    <div className="rounded-2xl bg-stone-100 p-5">
      <div className="flex items-center gap-3">
        <b className="text-4xl">{summary?.average_rating || "—"}</b>
        <div>
          <RatingStars value={summary?.average_rating} />
          <p className="text-sm text-stone-500">Based on {total} reviews</p>
        </div>
      </div>
      <div className="mt-4 space-y-1">
        {[5, 4, 3, 2, 1].map((n) => {
          const count = summary?.distribution?.[n] || 0;
          return (
            <div className="flex items-center gap-2 text-xs" key={n}>
              <span className="w-8">{n} ★</span>
              <div className="h-2 flex-1 overflow-hidden rounded bg-stone-200">
                <div
                  className="h-full bg-ink"
                  style={{ width: `${total ? (count / total) * 100 : 0}%` }}
                />
              </div>
              <span className="w-5">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
