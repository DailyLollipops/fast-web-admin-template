import { format } from "date-fns";

const colorPalette = [
  "primary",
  "secondary",
  "success",
  "error",
  "warning",
  "info",
] as const;

type MuiColor = (typeof colorPalette)[number];

export function alternateJoin(
  a: string[],
  b: string[],
  separator = "/",
): string {
  const result: string[] = [];

  const maxLength = Math.max(a.length, b.length);
  for (let i = 0; i < maxLength; i++) {
    if (i < a.length) result.push(a[i]);
    if (i < b.length) result.push(b[i]);
  }

  return result.join(separator);
}

export function stringToMuiColor(input: string): MuiColor {
  let hash = 1231;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 82) ^ input.charCodeAt(i);
  }
  const index = Math.abs(hash) % colorPalette.length;
  return colorPalette[index];
}

export function toCurrencyString(value: string): string {
  if (isNaN(+value)) {
    return "₱0.00";
  }

  return (+value).toLocaleString("en-US", {
    style: "currency",
    currency: "PHP",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export const formatCurrencyShort = (value: number) => {
  if (value >= 1_000_000) return `₱${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `₱${(value / 1_000).toFixed(1)}K`;
  return `₱${value.toFixed(0)}`;
};

export function snakeToCapitalizedWords(snake: string): string {
  return snake
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function getRelativeDate(date: Date): string {
  const now = new Date();
  const diffTime = now.getTime() - date.getTime();
  const differenceInDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (differenceInDays === 0) {
    return "Today";
  } else if (differenceInDays === 1) {
    return "Yesterday";
  } else if (differenceInDays < 7) {
    return `${differenceInDays} days ago`;
  } else if (differenceInDays < 30) {
    const weeks = Math.floor(differenceInDays / 7);
    return `${weeks} week${weeks > 1 ? "s" : ""} ago`;
  } else {
    return format(date, "MMMM dd, yyyy");
  }
}
