const DEFAULT_BASE_URL = "https://engine.prod.bria-api.com";

/** Resolved base URL + API token, filling gaps from the `BRIA_*` environment variables. */
export interface ResolvedSettings {
  baseUrl: string;
  apiToken: string | null;
}

/**
 * Resolve settings from explicit options, falling back to `BRIA_API_TOKEN` and `BRIA_BASE_URL`
 * (and finally the default engine URL). Explicit options always win.
 */
export function resolveSettings(opts: {
  baseUrl?: string | null;
  apiToken?: string | null;
}): ResolvedSettings {
  const env = typeof process !== "undefined" ? process.env : {};
  const rawBaseUrl = opts.baseUrl ?? env.BRIA_BASE_URL ?? DEFAULT_BASE_URL;
  return {
    baseUrl: rawBaseUrl.replace(/\/+$/, ""),
    apiToken: opts.apiToken ?? env.BRIA_API_TOKEN ?? null,
  };
}
