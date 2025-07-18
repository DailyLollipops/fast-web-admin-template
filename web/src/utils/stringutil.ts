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
