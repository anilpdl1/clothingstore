import { useEffect, useState } from "react";
import api from "../services/api";
import ProductCard from "../components/ProductCard";
export default function Products({ compact = false }) {
  const [data, setData] = useState({ items: [] }),
    [q, setQ] = useState("");
  useEffect(() => {
    api
      .get("/products", { params: { q, limit: compact ? 4 : 12 } })
      .then((r) => setData(r.data));
  }, [q, compact]);
  return (
    <section className={compact ? "" : "mx-auto max-w-7xl px-5 py-12"}>
      {!compact && (
        <>
          <h1 className="text-4xl font-bold">The collection</h1>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="mt-6 w-full rounded-xl border bg-white p-3 md:w-96"
            placeholder="Search pieces, brands…"
          />
        </>
      )}
      <div className="mt-8 grid grid-cols-2 gap-5 md:grid-cols-4">
        {data.items.map((p) => (
          <ProductCard product={p} key={p.id} />
        ))}
      </div>
      {!data.items.length && (
        <p className="py-16 text-center text-stone-500">
          No pieces match your search.
        </p>
      )}
    </section>
  );
}
