import { useState, useEffect } from "react";
import { getRecommendations } from "../services/api";
import ProductCard from "./ProductCard";

const RecommendationPanel = ({ userId, onProductClick }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [coldStart, setColdStart] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!userId) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const data = await getRecommendations(userId, 5);
        setRecommendations(data.recommendations || []);
        setColdStart(data.cold_start);
      } catch (err) {
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [userId]);

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-gray-800">
            🎯 Picked For You
          </h2>
          {coldStart && (
            <p className="text-xs text-gray-400 mt-0.5">
              Showing popular products — browse more to personalize
            </p>
          )}
        </div>
        {loading && (
          <span className="text-xs text-indigo-500 animate-pulse">
            Loading...
          </span>
        )}
      </div>

      {/* Empty State */}
      {!loading && recommendations.length === 0 && (
        <div className="text-center py-6 text-gray-400">
          <p className="text-sm">Browse products to get recommendations</p>
        </div>
      )}

      {/* Horizontal Scroll */}
      {!loading && recommendations.length > 0 && (
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
          {recommendations.map((product) => (
            <div key={product.product_id} className="min-w-[160px] max-w-[160px]">
              <ProductCard
                {...product}
                onClick={() => onProductClick && onProductClick(product)}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationPanel;