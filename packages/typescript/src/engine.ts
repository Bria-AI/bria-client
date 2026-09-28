import { BriaException } from "./toolkit/errors.js";
import { BriaResponse } from "./toolkit/response.js";
import { VERSION } from "./version.js";

// POST is never retried: a `run`/`submit` that timed out or got a 5xx may already have started a job.
const RETRYABLE_STATUS = new Set([429, 502, 503, 504]);
const RETRYABLE_METHODS: ReadonlySet<HttpMethod> = new Set<HttpMethod>(["GET"]);
const DEFAULT_REQUEST_TIMEOUT_SECONDS = 30;

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
  private readonly requestTimeoutMs: number;

  constructor(opts: {
    baseUrl: string;
    apiToken: string | null;
    defaultHeaders?: Record<string, string>;
    retry?: RetryConfig;
    /** Per-request timeout in seconds (default 30, matching the Python SDK). */
    requestTimeout?: number;
  }) {
    this.baseUrl = opts.baseUrl;
    this.apiToken = opts.apiToken;
    this.defaultHeaders = opts.defaultHeaders ?? {};
    this.retry = opts.retry ?? DEFAULT_RETRY;
    const timeout = opts.requestTimeout ?? DEFAULT_REQUEST_TIMEOUT_SECONDS;
    if (!Number.isFinite(timeout) || timeout <= 0) {
      throw new Error(`requestTimeout must be a positive number of seconds, got ${timeout}`);
    }
    this.requestTimeoutMs = timeout * 1000;
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

  prepareEndpoint(endpoint: string): string {
    const trimmed = endpoint.replace(/^\/+|\/+$/g, "");
    const withoutV2 = trimmed === "v2" ? "" : trimmed.replace(/^v2\//, "");
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

    const init: RequestInit = { method: args.method, headers };
    if (args.method === "POST") {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(payload ?? {});
    }

    const maxAttempts = RETRYABLE_METHODS.has(args.method) ? this.retry.total + 1 : 1;
    let lastNetworkError: unknown = null;
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const timer = new TimeoutSignal(this.requestTimeoutMs, args.signal);
      try {
        const res = await fetch(url, { ...init, signal: timer.signal });
        if (RETRYABLE_STATUS.has(res.status) && attempt < maxAttempts - 1) {
          await sleep(retryAfterMs(res) ?? this.backoffMs(attempt));
          continue;
        }
        return await toBriaResponse(res);
      } catch (e) {
        if (args.signal?.aborted) throw e;
        if (timer.timedOut) {
          lastNetworkError = new BriaException({
            statusCode: 408,
            message: "Request timeout",
            details: `No response within ${this.requestTimeoutMs / 1000}s: ${url}`,
          });
        } else {
          lastNetworkError = e;
        }
        if (attempt < maxAttempts - 1) {
          await sleep(this.backoffMs(attempt));
          continue;
        }
      } finally {
        timer.clear();
      }
    }

    if (lastNetworkError instanceof BriaException) throw lastNetworkError;
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

/**
 * An AbortSignal that fires after `ms`, or when the caller's own signal fires. Node 18 has no
 * `AbortSignal.any`, hence the manual link.
 */
class TimeoutSignal {
  readonly signal: AbortSignal;
  timedOut = false;
  private readonly controller = new AbortController();
  private readonly timer: ReturnType<typeof setTimeout>;
  private readonly outer: AbortSignal | undefined;
  private readonly onOuterAbort = () => this.controller.abort();

  constructor(ms: number, outer?: AbortSignal) {
    this.signal = this.controller.signal;
    this.outer = outer;
    this.timer = setTimeout(() => {
      this.timedOut = true;
      this.controller.abort();
    }, ms);
    if (outer) {
      if (outer.aborted) this.controller.abort();
      else outer.addEventListener("abort", this.onOuterAbort, { once: true });
    }
  }

  clear(): void {
    clearTimeout(this.timer);
    this.outer?.removeEventListener("abort", this.onOuterAbort);
  }
}

/** Numeric `Retry-After` header, in seconds. */
function retryAfterMs(res: Response): number | null {
  const raw = res.headers.get("retry-after");
  if (raw === null) return null;
  const seconds = Number(raw);
  return Number.isFinite(seconds) && seconds >= 0 ? seconds * 1000 : null;
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
