import { useEffect, useState } from "react";
import api from "../services/api";
import { useCart } from "../context/CartContext";

function submitEsewaForm({ form_url: formUrl, fields }) {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = formUrl;
  Object.entries(fields).forEach(([name, value]) => {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.value = String(value);
    form.appendChild(input);
  });
  document.body.appendChild(form);
  form.submit();
}

export default function Checkout() {
  const [addresses, setAddresses] = useState([]);
  const [address, setAddress] = useState("");
  const [form, setForm] = useState({
    line1: "",
    city: "",
    state: "",
    postal_code: "",
  });
  const [message, setMessage] = useState("");
  const { cart } = useCart();

  async function loadAddresses() {
    const response = await api.get("/addresses");
    setAddresses(response.data);
    if (response.data[0])
      setAddress(
        String(
          response.data.find((item) => item.is_default)?.id ||
            response.data[0].id,
        ),
      );
  }

  useEffect(() => {
    void loadAddresses().catch(() =>
      setMessage("Could not load delivery addresses."),
    );
  }, []);

  async function saveAddress() {
    const response = await api.post("/addresses", form);
    await loadAddresses();
    setAddress(String(response.data.id));
  }

  async function pay() {
    if (!address) return setMessage("Add and select a delivery address.");
    setMessage("Redirecting securely to eSewa…");
    try {
      const response = await api.post("/payments/create-order", {
        address_id: +address,
      });
      submitEsewaForm(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  return (
    <section className="mx-auto grid max-w-5xl gap-10 px-5 py-12 md:grid-cols-2">
      <div>
        <h1 className="text-4xl font-bold">Checkout</h1>
        <h2 className="mt-8 text-xl font-bold">Delivery address</h2>
        {addresses.map((item) => (
          <label className="mt-3 block rounded-xl border p-4" key={item.id}>
            <input
              type="radio"
              checked={address === String(item.id)}
              onChange={() => setAddress(String(item.id))}
            />{" "}
            <span className="ml-2">
              {item.line1}, {item.city}, {item.state} {item.postal_code}
            </span>
          </label>
        ))}
        <div className="mt-5 grid gap-3">
          <input
            placeholder="Address line"
            onChange={(event) =>
              setForm({ ...form, line1: event.target.value })
            }
          />
          <input
            placeholder="City"
            onChange={(event) => setForm({ ...form, city: event.target.value })}
          />
          <input
            placeholder="State"
            onChange={(event) =>
              setForm({ ...form, state: event.target.value })
            }
          />
          <input
            placeholder="Postal code"
            onChange={(event) =>
              setForm({ ...form, postal_code: event.target.value })
            }
          />
          <button onClick={saveAddress} className="rounded-full border py-2">
            Save address
          </button>
        </div>
      </div>
      <aside className="h-fit rounded-2xl bg-stone-100 p-6">
        <h2 className="text-xl font-bold">Order total: रू{cart.total}</h2>
        <p className="mt-3 text-sm text-stone-600">
          You will be securely redirected to eSewa to complete payment. We
          confirm the order only after eSewa signature and status verification.
        </p>
        {message && <p className="mt-4 text-sm">{message}</p>}
        <button
          onClick={pay}
          className="mt-6 w-full rounded-full bg-ink py-3 text-white"
        >
          Pay with eSewa
        </button>
      </aside>
    </section>
  );
}
