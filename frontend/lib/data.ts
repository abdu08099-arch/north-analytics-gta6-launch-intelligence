// Reads the data products at build time. Runs on the server only.
// A missing product returns null, and every page shows an honest empty state for it.
import { readFileSync } from "node:fs";
import path from "node:path";
import type { Envelope, Products } from "./types";

export const PRODUCTS_DIR =
  process.env.DATA_PRODUCTS_DIR || path.join(process.cwd(), "..", "data", "products");

function load<T>(file: string, dir = PRODUCTS_DIR): Envelope<T> | null {
  try {
    const parsed = JSON.parse(readFileSync(path.join(dir, file), "utf8")) as Envelope<T>;
    if (!parsed || !Array.isArray(parsed.data)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function loadProducts(dir = PRODUCTS_DIR): Products {
  return {
    status: load("status.json", dir),
    events: load("events.json", dir),
    coverage: load("news_coverage_daily.json", dir),
    search: load("search_interest.json", dir),
  };
}
