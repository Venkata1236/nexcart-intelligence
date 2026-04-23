import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import Spinner from "./ui/Spinner";

const ProductGrid = ({ userId, filterSentiment, onProductClick }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8000/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, n: 20 }),
        });
        const data = await response.json();
        setProducts(data.recommendations || []);
      } catch (err) {
        setError("Failed to load products");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [userId]);

  // Client-side sentiment filter
  const filtered = products.filter((p) => {
    if (!filterSentiment || filterSentiment === "all") return true;
    if (filterSentiment === "positive") return p.sentiment_score > 0.75;
    if (filterSentiment === "mixed")
      return p.sentiment_score >= 0.45 && p.sentiment_score <= 0.75;
    if (filterSentiment === "negative") return p.sentiment_score < 0.45;
    return true;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 py-10">
        <p>{error}</p>
      </div>
    );
  }

  if (filtered.length === 0) {
    return (
      <div className="text-center text-gray-400 py-10">
        <p className="text-lg">No products match this filter.</p>
        <p className="text-sm mt-1">Try selecting a different sentiment.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {filtered.map((product) => (
        <ProductCard
          key={product.product_id}
          {...product}
          onClick={() => onProductClick && onProductClick(product)}
        />
      ))}
    </div>
  );
};

export default ProductGrid;