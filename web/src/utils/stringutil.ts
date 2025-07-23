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
