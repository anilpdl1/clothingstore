import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
export default function Cart() {
  const { cart, update, remove } = useCart();
  if (!cart.items?.length)
    return (
      <section className="mx-auto max-w-3xl px-5 py-20 text-center">
        <h1 className="text-4xl font-bold">Your bag is empty.</h1>
        <Link className="mt-6 inline-block underline" to="/products">
          Find your next favorite
        </Link>
      </section>
    );
  return (
    <section className="mx-auto grid max-w-5xl gap-10 px-5 py-12 md:grid-cols-[1fr_320px]">
      <div>
        <h1 className="mb-7 text-4xl font-bold">Your bag</h1>
        {cart.items.map((i) => (
          <article className="mb-5 flex gap-4 border-b pb-5" key={i.id}>
            <img
              className="h-28 w-24 object-cover"
              src={
                i.product.image_url ||
                "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=200"
              }
            />
            <div className="flex-1">
              <h2 className="font-bold">{i.product.name}</h2>
              <p className="text-sm text-stone-500">
                {i.color} · {i.size}
              </p>
              <p>₹{i.unit_price}</p>
              <div className="mt-3 flex gap-3">
                <button
                  onClick={() => update(i.id, Math.max(1, i.quantity - 1))}
                >
                  −
                </button>
                <span>{i.quantity}</span>
                <button
                  onClick={() =>
                    update(i.id, Math.min(i.stock, i.quantity + 1))
                  }
                >
                  +
                </button>
                <button
                  className="ml-4 text-sm underline"
                  onClick={() => remove(i.id)}
                >
                  Remove
                </button>
              </div>
            </div>
            <b>₹{i.line_total}</b>
          </article>
        ))}
      </div>
      <aside className="h-fit rounded-2xl bg-stone-100 p-6">
        <h2 className="text-xl font-bold">Summary</h2>
        <div className="mt-5 space-y-2">
          <p className="flex justify-between">
            <span>Subtotal</span>
            <span>₹{cart.subtotal}</span>
          </p>
          <p className="flex justify-between">
            <span>Shipping</span>
            <span>₹{cart.shipping}</span>
          </p>
          <p className="flex justify-between border-t pt-3 font-bold">
            <span>Total</span>
            <span>₹{cart.total}</span>
          </p>
        </div>
        <Link
          to="/checkout"
          className="mt-6 block rounded-full bg-ink py-3 text-center text-white"
        >
          Secure checkout
        </Link>
      </aside>
    </section>
  );
}
