import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import RatingStars from '../components/RatingStars';
import RecommendationCarousel from '../components/RecommendationCarousel';
import ReviewList from '../components/ReviewList';

export default function Detail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { add } = useCart();
  const { user } = useAuth();
  const [product, setProduct] = useState();
  const [variant, setVariant] = useState();
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadProduct() {
      try {
        const response = await api.get(`/products/${id}`);
        if (cancelled) return;
        setProduct(response.data);
        setVariant(response.data.variants.find((item) => item.stock_quantity > 0));

        if (localStorage.token) {
          void api.post(`/products/${id}/interactions?event_type=VIEW`).catch(() => {});
        }
      } catch {
        if (!cancelled) setError('Could not load this product.');
      }
    }

    void loadProduct();
    return () => { cancelled = true; };
  }, [id]);

  if (!product) return <div className="p-20 text-center">{error || 'Loading piece…'}</div>;

  const options = product.variants.filter((item) => item.stock_quantity > 0);

  async function addToCart() {
    if (!user) return navigate('/login');
    if (!variant) return setError('This product is currently out of stock.');
    try {
      await add(variant.id, quantity);
      navigate('/cart');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not add item');
    }
  }

  return <section className="mx-auto max-w-7xl px-5 py-10"><div className="grid gap-10 md:grid-cols-2"><img className="aspect-[3/4] w-full object-cover" src={product.image_url || 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900'} alt={product.name} /><div><p className="text-sm uppercase tracking-widest text-moss">{product.brand}</p><h1 className="mt-2 text-4xl font-bold">{product.name}</h1><div className="mt-3 flex items-center gap-2"><RatingStars value={product.rating?.average_rating} small /><span className="text-sm text-stone-600">{product.rating?.average_rating || 0} ({product.rating?.total_reviews || 0} reviews)</span></div><p className="mt-3 text-2xl">₹{product.discount_price || product.price}</p><p className="mt-6 leading-7 text-stone-600">{product.description}</p><div className="mt-8"><p className="mb-3 font-bold">Choose a variant</p><div className="flex flex-wrap gap-2">{options.map((item) => <button onClick={() => setVariant(item)} className={`rounded-full border px-4 py-2 ${variant?.id === item.id ? 'border-ink bg-ink text-white' : ''}`} key={item.id}>{item.color} · {item.size}</button>)}</div></div><div className="mt-6 flex items-center gap-4"><button onClick={() => setQuantity(Math.max(1, quantity - 1))}>−</button><span>{quantity}</span><button onClick={() => setQuantity(Math.min(variant?.stock_quantity || 1, quantity + 1))}>+</button></div>{error && <p className="mt-3 text-red-600">{error}</p>}<button className="mt-7 w-full rounded-full bg-ink py-4 font-semibold text-white" onClick={addToCart}>Add to bag</button></div></div><ReviewList productId={id} /><RecommendationCarousel productId={id} /></section>;
}
