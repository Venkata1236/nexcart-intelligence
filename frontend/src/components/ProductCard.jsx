import SentimentBadge from "./SentimentBadge";

const ProductCard = ({
  product_id,
  avg_rating,
  sentiment_score,
  review_count,
  is_hidden_gem,
  onClick,
}) => {
  const stars = Math.round(avg_rating || 0);

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-2xl p-4 cursor-pointer
        hover:shadow-lg hover:scale-[1.02] transition-all duration-200 relative"
    >
      {/* Hidden Gem Badge */}
      {is_hidden_gem && (
        <span className="absolute top-3 right-3 bg-purple-100 text-purple-700
          text-xs font-semibold px-2 py-0.5 rounded-full border border-purple-300">
          💎 Hidden Gem
        </span>
      )}

      {/* Product ID */}
      <p className="text-xs text-gray-400 font-mono mb-1 truncate">
        {product_id}
      </p>

      {/* Star Rating */}
      <div className="flex items-center gap-1 mb-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`text-lg ${
              star <= stars ? "text-amber-400" : "text-gray-200"
            }`}
          >
            ★
          </span>
        ))}
        <span className="text-sm text-gray-500 ml-1">
          {avg_rating ? avg_rating.toFixed(1) : "N/A"}
        </span>
      </div>

      {/* Sentiment Badge */}
      <div className="mb-3">
        <SentimentBadge sentiment_score={sentiment_score || 0} size="sm" />
      </div>

      {/* Review Count */}
      <p className="text-xs text-gray-400">
        {review_count} {review_count === 1 ? "review" : "reviews"}
      </p>
    </div>
  );
};

export default ProductCard;