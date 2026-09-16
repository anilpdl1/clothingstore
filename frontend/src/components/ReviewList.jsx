import { useEffect, useState } from "react";
import api from "../services/api";
import RatingSummary from "./RatingSummary";
import ReviewCard from "./ReviewCard";
import ReviewForm from "./ReviewForm";
export default function ReviewList({ productId }) {
  const [data, setData] = useState({ items: [], summary: {} }),
    [rating, setRating] = useState(""),
    [sort, setSort] = useState("recent");
  const load = () =>
    api
      .get(`/products/${productId}/reviews`, {
        params: { rating: rating || undefined, sort },
      })
      .then((r) => setData(r.data));
  useEffect(() => {
    void load();
  }, [productId, rating, sort]);
  return (
    <section className="mt-14 border-t pt-10">
      <h2 className="text-3xl font-bold">Customer reviews</h2>
      <div className="mt-6 grid gap-7 md:grid-cols-[280px_1fr]">
        <div>
          <RatingSummary summary={data.summary} />
          <ReviewForm productId={productId} onCreated={load} />
        </div>
        <div>
          <div className="flex gap-3">
            <select value={rating} onChange={(e) => setRating(e.target.value)}>
              <option value="">All reviews</option>
              {[5, 4, 3, 2, 1].map((x) => (
                <option value={x} key={x}>
                  {x} stars
                </option>
              ))}
            </select>
            <select value={sort} onChange={(e) => setSort(e.target.value)}>
              <option value="recent">Most recent</option>
              <option value="highest">Highest rating</option>
              <option value="lowest">Lowest rating</option>
              <option value="helpful">Most helpful</option>
            </select>
          </div>
          {data.items.length ? (
            data.items.map((r) => (
              <ReviewCard review={r} onChanged={load} key={r.id} />
            ))
          ) : (
            <p className="py-8 text-stone-500">
              No reviews yet. Be the first verified customer to share your
              experience.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
