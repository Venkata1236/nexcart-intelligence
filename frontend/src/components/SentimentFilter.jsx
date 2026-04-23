const FILTERS = [
  { key: "all", label: "All", emoji: "🛍️" },
  { key: "positive", label: "Positive", emoji: "😊" },
  { key: "mixed", label: "Mixed", emoji: "😐" },
  { key: "negative", label: "Critical", emoji: "😞" },
];

const SentimentFilter = ({ selected, onChange }) => {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-sm text-gray-500 font-medium mr-1">Filter:</span>
      {FILTERS.map((filter) => {
        const isSelected = selected === filter.key;
        return (
          <button
            key={filter.key}
            onClick={() => onChange(filter.key)}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full
              text-sm font-medium border transition-all duration-200
              ${
                isSelected
                  ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                  : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400 hover:text-indigo-600"
              }`}
          >
            <span>{filter.emoji}</span>
            {filter.label}
          </button>
        );
      })}
    </div>
  );
};

export default SentimentFilter;