import { BriaResponse } from "./toolkit/response.js";
import { VERSION } from "./version.js";

const RETRYABLE_STATUS = new Set([429, 500, 502, 503, 504]);

/** Retry policy for transient failures. Defaults mirror the Python SDK (`total: 3`, `backoffFactor: 2`). */
export interface RetryConfig {
  total: number;
  backoffFactor: number;
}

export const DEFAULT_RETRY: RetryConfig = { total: 3, backoffFactor: 2 };

export type HttpMethod = "GET" | "POST";

/**
 * The HTTP layer: endpoint/header/payload preparation, auth, and a fetch-based request with
 * retries. Mirrors the Python `ApiEngine` + `BriaEngine`.
 */
export class ApiEngine {
  readonly baseUrl: string;
  private readonly apiToken: string | null;
  private readonly defaultHeaders: Record<string, string>;
  private readonly retry: RetryConfig;

  constructor(opts: {
    baseUrl: string;
    apiToken: string | null;
    defaultHeaders?: Record<string, string>;
    retry?: RetryConfig;
  }) {
    this.baseUrl = opts.baseUrl;
    this.apiToken = opts.apiToken;
    this.defaultHeaders = opts.defaultHeaders ?? {};
    this.retry = opts.retry ?? DEFAULT_RETRY;
  }

  get userAgentHeaders(): Record<string, string> {
    return { "User-Agent": `BriaSDK/${VERSION} (js)` };
  }

  private get authHeaders(): Record<string, string> {
    if (this.apiToken === null) {
      throw new Error(
        "api_token is required, please set BRIA_API_TOKEN or pass it explicitly to the method",
      );
    }
    return { api_token: this.apiToken };
  }

  /** Resolve the auth headers for a call, honoring a per-call token override. */
  checkAuthOverride(callApiToken?: string): Record<string, string> | null {
    const token = callApiToken ?? this.apiToken;
    return token ? { api_token: token } : null;
  }

  /** Strip a leading `/`, drop a leading `v2` segment, then prefix `/v2/`. */
  prepareEndpoint(endpoint: string): string {
    const trimmed = endpoint.replace(/^\/+|\/+$/g, "");
    const withoutV2 = trimmed.startsWith("v2") ? trimmed.slice(2) : trimmed;
    const clean = withoutV2.replace(/^\/+|\/+$/g, "");
    return `${this.baseUrl}/v2/${clean}`;
  }

  prepareHeaders(
    headers?: Record<string, string>,
    authOverride?: Record<string, string> | null,
  ): Record<string, string> {
    const auth = authOverride ?? this.authHeaders;
    return { ...this.userAgentHeaders, ...this.defaultHeaders, ...(headers ?? {}), ...auth };
  }

  /** Drop top-level keys whose value is null/undefined. */
  static preparePayload(
    payload: Record<string, unknown> | null | undefined,
  ): Record<string, unknown> | null {
    if (payload === null || payload === undefined) return null;
    return Object.fromEntries(
      Object.entries(payload).filter(([, v]) => v !== null && v !== undefined),
    );
  }

  async request(args: {
    endpoint: string;
    method: HttpMethod;
    payload?: Record<string, unknown> | null;
    params?: Record<string, unknown> | null;
    headers?: Record<string, string>;
    authOverride?: Record<string, string> | null;
    signal?: AbortSignal;
  }): Promise<BriaResponse> {
    let url = this.prepareEndpoint(args.endpoint);
    if (args.params) {
      const qs = new URLSearchParams();
      for (const [k, v] of Object.entries(args.params)) {
        if (v !== null && v !== undefined) qs.append(k, String(v));
      }
      const query = qs.toString();
      if (query) url += `?${query}`;
    }

    const headers = this.prepareHeaders(args.headers, args.authOverride);
    const payload = ApiEngine.preparePayload(args.payload);

    const init: RequestInit = { method: args.method, headers, signal: args.signal };
    if (args.method === "POST") {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(payload ?? {});
    }

    let lastNetworkError: unknown = null;
    for (let attempt = 0; attempt <= this.retry.total; attempt++) {
      try {
        const res = await fetch(url, init);
        if (RETRYABLE_STATUS.has(res.status) && attempt < this.retry.total) {
          await sleep(this.backoffMs(attempt));
          continue;
        }
        return await toBriaResponse(res);
      } catch (e) {
        lastNetworkError = e;
        if (attempt < this.retry.total) {
          await sleep(this.backoffMs(attempt));
          continue;
        }
      }
    }

    // Connection failed after exhausting retries — mirror Python's ServerConnectionError (503).
    return BriaResponse.fromError({
      code: 503,
      message: "Connection error",
      details: `Failed to connect to the server: ${url}${
        lastNetworkError ? ` (${String(lastNetworkError)})` : ""
      }`,
    });
  }

  private backoffMs(attempt: number): number {
    return this.retry.backoffFactor * 2 ** attempt * 1000;
  }
}

async function toBriaResponse(res: Response): Promise<BriaResponse> {
  const bodyText = await res.text();
  let body: unknown = null;
  try {
    body = bodyText ? JSON.parse(bodyText) : null;
  } catch {
    body = null;
  }
  const headers: Record<string, string> = {};
  res.headers.forEach((value, key) => {
    headers[key] = value;
  });
  return BriaResponse.fromHttpResponse({
    statusCode: res.status,
    reasonPhrase: res.statusText,
    body,
    bodyText,
    headers,
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
