import { useEffect, useState } from "react";
import api from "../services/api";
import ProductCard from "./ProductCard";
export default function RecommendationCarousel({
  productId,
  title = "You may also like",
}) {
  const [items, setItems] = useState([]);
  useEffect(() => {
    const url = productId
      ? `/products/${productId}/similar`
      : "/recommendations";
    api
      .get(url)
      .then((r) => setItems(r.data.items))
      .catch(() => {});
  }, [productId]);
  if (!items.length) return null;
  return (
    <section className="mt-14">
      <h2 className="text-3xl font-bold">{title}</h2>
      <div className="mt-6 flex gap-5 overflow-x-auto pb-3">
        {items.map((p) => (
          <div className="w-48 shrink-0" key={p.id}>
            <ProductCard product={p} />
            {p.rating && <p className="text-sm text-amber-600">★ {p.rating}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}
