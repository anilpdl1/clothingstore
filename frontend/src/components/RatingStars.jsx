export default function RatingStars({ value = 0, onChange, small = false }) {
  return (
    <span
      className={`inline-flex ${small ? "text-sm" : "text-xl"} tracking-tight ${onChange ? "cursor-pointer" : ""}`}
      aria-label={`${value} out of 5 stars`}
    >
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          type="button"
          disabled={!onChange}
          onClick={() => onChange(star)}
          key={star}
          className={
            star <= Math.round(value) ? "text-amber-500" : "text-stone-300"
          }
        >
          ★
        </button>
      ))}
    </span>
  );
}
