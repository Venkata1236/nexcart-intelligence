const SentimentBadge = ({ sentiment_score, size = "md" }) => {
  const getConfig = (score) => {
    if (score > 0.75)
      return {
        label: "Positive",
        emoji: "😊",
        bg: "bg-emerald-100",
        text: "text-emerald-700",
        border: "border-emerald-300",
        dot: "bg-emerald-500",
      };
    if (score >= 0.45)
      return {
        label: "Mixed",
        emoji: "😐",
        bg: "bg-amber-100",
        text: "text-amber-700",
        border: "border-amber-300",
        dot: "bg-amber-500",
      };
    return {
      label: "Critical",
      emoji: "😞",
      bg: "bg-red-100",
      text: "text-red-700",
      border: "border-red-300",
      dot: "bg-red-500",
    };
  };

  const sizeClasses = {
    sm: "text-xs px-2 py-0.5 gap-1",
    md: "text-sm px-3 py-1 gap-1.5",
    lg: "text-base px-4 py-1.5 gap-2",
  };

  const config = getConfig(sentiment_score);

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium
        ${config.bg} ${config.text} ${config.border} ${sizeClasses[size]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.emoji} {config.label}
    </span>
  );
};

export default SentimentBadge;