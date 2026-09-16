import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import Home from "./pages/Home";
import Products from "./pages/Products";
import Detail from "./pages/Detail";
import Cart from "./pages/Cart";
import Login from "./pages/Login";
import Checkout from "./pages/Checkout";
import Profile from "./pages/Profile";
import Admin from "./pages/Admin";
import AdminReviews from "./pages/AdminReviews";
function Protected({ children, admin = false }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-20 text-center">Loading…</div>;
  return user && (!admin || user.role === "ADMIN") ? (
    children
  ) : (
    <Navigate to="/login" replace />
  );
}
export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<Detail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/checkout"
          element={
            <Protected>
              <Checkout />
            </Protected>
          }
        />
        <Route
          path="/profile"
          element={
            <Protected>
              <Profile />
            </Protected>
          }
        />
        <Route
          path="/admin"
          element={
            <Protected admin>
              <Admin />
            </Protected>
          }
        />
        <Route
          path="/admin/reviews"
          element={
            <Protected admin>
              <AdminReviews />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Layout>
  );
}
