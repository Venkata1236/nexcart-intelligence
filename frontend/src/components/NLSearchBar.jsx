import { useState } from "react";
import { queryAgent } from "../services/api";
import ProductCard from "./ProductCard";

const NLSearchBar = ({ userId }) => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setProducts([]);

    try {
      const data = await queryAgent(userId, query);
      setResponse(data.response);
      setProducts(
        data.products_mentioned.map((id) => ({
          product_id: id,
          avg_rating: 0,
          sentiment_score: 0.5,
          review_count: 0,
          is_hidden_gem: false,
        }))
      );
    } catch (err) {
      setError("Agent query failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className="w-full">
      {/* Search Input */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Try: "Show me products with great reviews..."'
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3
            text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400
            focus:border-transparent transition-all"
        />
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300
            text-white px-6 py-3 rounded-xl text-sm font-medium
            transition-colors duration-200"
        >
          {loading ? "..." : "Ask AI"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <p className="text-red-500 text-sm mb-3">{error}</p>
      )}

      {/* Agent Response */}
      {response && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 mb-4">
          <p className="text-xs font-semibold text-indigo-500 mb-1">
            🤖 NexCart AI
          </p>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{response}</p>
        </div>
      )}

      {/* Products Mentioned */}
      {products.length > 0 && (
        <div>
          <p className="text-xs text-gray-400 mb-2">
            Products mentioned ({products.length})
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {products.map((p) => (
              <ProductCard key={p.product_id} {...p} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default NLSearchBar;