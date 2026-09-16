import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
export default function Admin() {
  const [d, setD] = useState(),
    [orders, setOrders] = useState([]);
  useEffect(() => {
    api.get("/admin/dashboard").then((r) => setD(r.data));
    api.get("/admin/orders").then((r) => setOrders(r.data));
  }, []);
  if (!d) return <div className="p-20">Loading dashboard…</div>;
  return (
    <section className="mx-auto max-w-7xl px-5 py-10">
      <p className="text-sm font-bold uppercase tracking-widest text-moss">
        Administration
      </p>
      <h1 className="mt-2 text-4xl font-bold">Store overview</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Revenue", `₹${d.total_revenue}`],
          ["Orders", d.total_orders],
          ["Customers", d.total_users],
          ["Products", d.total_products],
        ].map((x) => (
          <div className="rounded-2xl bg-[#d9dfd0] p-6" key={x[0]}>
            <p className="text-sm">{x[0]}</p>
            <b className="text-3xl">{x[1]}</b>
          </div>
        ))}
      </div>
      <div className="mt-7 rounded-2xl bg-stone-100 p-6">
        <div className="flex justify-between">
          <h2 className="text-xl font-bold">Review quality</h2>
          <Link className="underline" to="/admin/reviews">
            Moderate reviews →
          </Link>
        </div>
        <p className="mt-3">
          ★ {d.review_analytics.average_store_rating} average ·{" "}
          {d.review_analytics.total_reviews} reviews ·{" "}
          {d.review_analytics.reported_reviews} open reports
        </p>
      </div>
      <h2 className="mt-12 text-2xl font-bold">Recent orders</h2>
      <div className="mt-4 overflow-auto rounded-xl border">
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.order_number}</td>
                <td>{o.customer}</td>
                <td>₹{o.total}</td>
                <td>{o.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2 className="mt-12 text-2xl font-bold">Low stock</h2>
      {d.low_stock.map((v) => (
        <p className="mt-2" key={v.id}>
          {v.product} ({v.sku}) — {v.stock_quantity} remaining
        </p>
      ))}
    </section>
  );
}
