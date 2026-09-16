import { Link } from "react-router-dom";
import Products from "./Products";
import RecommendationCarousel from "../components/RecommendationCarousel";
export default function Home() {
  return (
    <>
      <section className="grid min-h-[65vh] bg-[#d9dfd0] md:grid-cols-2">
        <div className="flex flex-col justify-center px-8 py-16 md:px-20">
          <p className="mb-4 text-sm font-bold uppercase tracking-[.22em] text-moss">
            Autumn / Winter 2026
          </p>
          <h1 className="max-w-xl text-5xl font-black leading-[.95] tracking-tight md:text-7xl">
            Wear what feels like you.
          </h1>
          <p className="mt-6 max-w-md text-lg text-stone-700">
            Essential pieces, honest materials and silhouettes that move with
            your life.
          </p>
          <Link
            to="/products"
            className="mt-8 w-fit rounded-full bg-ink px-6 py-3 text-white"
          >
            Explore collection
          </Link>
        </div>
        <img
          className="h-full min-h-[360px] w-full object-cover"
          alt="Editorial clothing"
          src="https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1200"
        />
      </section>
      <section className="mx-auto max-w-7xl px-5 py-16">
        <div className="mb-8 flex justify-between">
          <h2 className="text-3xl font-bold">New arrivals</h2>
          <Link to="/products">View all →</Link>
        </div>
        <Products compact />
        <RecommendationCarousel title="Recommended for you" />
      </section>
    </>
  );
}
