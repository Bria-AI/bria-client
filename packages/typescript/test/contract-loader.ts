import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

// packages/typescript/test -> repo root -> contract
const here = dirname(fileURLToPath(import.meta.url));
export const CONTRACT_DIR = resolve(here, "..", "..", "..", "contract");

export function loadContract<T = any>(relativePath: string): T {
  return JSON.parse(readFileSync(resolve(CONTRACT_DIR, relativePath), "utf-8")) as T;
}
