import { useState } from "react";
import RecommendationPanel from "../components/RecommendationPanel";
import ProductGrid from "../components/ProductGrid";
import SentimentFilter from "../components/SentimentFilter";
import NLSearchBar from "../components/NLSearchBar";

const DEFAULT_USER = "A3SGXH7AUHU8GW";

const StorePage = () => {
  const [userId] = useState(DEFAULT_USER);
  const [filterSentiment, setFilterSentiment] = useState("all");
  const [selectedProduct, setSelectedProduct] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🛒</span>
            <h1 className="text-xl font-bold text-gray-900">
              NexCart Intelligence
            </h1>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            user: {userId}
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* NL Search */}
        <div className="mb-6">
          <p className="text-sm font-medium text-gray-600 mb-2">
            🤖 Ask AI anything about products
          </p>
          <NLSearchBar userId={userId} />
        </div>

        {/* Recommendations */}
        <RecommendationPanel
          userId={userId}
          onProductClick={setSelectedProduct}
        />

        {/* Filter + Grid */}
        <div className="mb-4">
          <SentimentFilter
            selected={filterSentiment}
            onChange={setFilterSentiment}
          />
        </div>

        <ProductGrid
          userId={userId}
          filterSentiment={filterSentiment}
          onProductClick={setSelectedProduct}
        />
      </main>

      {/* Simple Product Detail Modal */}
      {selectedProduct && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center
            justify-center z-50 p-4"
          onClick={() => setSelectedProduct(null)}
        >
          <div
            className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-4">
              <h2 className="font-semibold text-gray-800">Product Detail</h2>
              <button
                onClick={() => setSelectedProduct(null)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >
                ×
              </button>
            </div>
            <p className="text-xs font-mono text-gray-500 mb-2">
              {selectedProduct.product_id}
            </p>
            <p className="text-sm text-gray-600">
              ⭐ Rating: {selectedProduct.avg_rating?.toFixed(1) || "N/A"}
            </p>
            <p className="text-sm text-gray-600">
              📝 Reviews: {selectedProduct.review_count}
            </p>
            {selectedProduct.is_hidden_gem && (
              <p className="text-sm text-purple-600 mt-2">
                💎 Hidden Gem product
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StorePage;