import { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    api.get('/orders').then((response) => setOrders(response.data)).catch(() => setOrders([]));
  }, []);

  return <section className="mx-auto max-w-5xl px-5 py-12"><h1 className="text-4xl font-bold">Hello, {user?.name}</h1><p className="mt-2 text-stone-600">{user?.email}</p><h2 className="mt-12 text-2xl font-bold">Order history</h2>{orders.length ? orders.map((order) => <article className="mt-4 rounded-xl border p-5" key={order.id}><div className="flex justify-between"><b>{order.order_number}</b><span>{order.order_status}</span></div><p className="mt-2 text-sm">{order.items.map((item) => `${item.product_name} × ${item.quantity}`).join(', ')}</p><p className="mt-2">₹{order.total_amount} · {order.payment_status}</p></article>) : <p className="mt-5 text-stone-500">No orders yet.</p>}</section>;
}
