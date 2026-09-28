import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiEngine } from "../src/engine.js";
import { BriaException } from "../src/toolkit/errors.js";

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

function engine(opts: { requestTimeout?: number } = {}): ApiEngine {
  return new ApiEngine({
    baseUrl: "https://x",
    apiToken: "t",
    retry: { total: 3, backoffFactor: 0 },
    ...opts,
  });
}

/** fetch stub that answers with the given HTTP statuses in order, then 200 forever. */
function fetchSequence(statuses: number[], headers: Record<string, string> = {}) {
  let n = 0;
  const fn = vi.fn(async () => {
    const status = statuses[n] ?? 200;
    n++;
    const body =
      status >= 400
        ? { error: { code: status, message: "err", details: "d" } }
        : { request_id: "r", result: { ok: true } };
    return new Response(JSON.stringify(body), { status, headers });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("ApiEngine retry", () => {
  it("never retries a POST, even on a retryable status", async () => {
    const fetchFn = fetchSequence([503, 200]);
    const res = await engine().request({ endpoint: "x", method: "POST", payload: {} });
    expect(fetchFn).toHaveBeenCalledTimes(1);
    expect(res.error?.code).toBe(503);
  });

  it("never retries a POST on a network error", async () => {
    const fetchFn = vi.fn(async () => {
      throw new TypeError("fetch failed");
    });
    vi.stubGlobal("fetch", fetchFn);
    const res = await engine().request({ endpoint: "x", method: "POST", payload: {} });
    expect(fetchFn).toHaveBeenCalledTimes(1);
    expect(res.error?.code).toBe(503);
    expect(res.error?.message).toBe("Connection error");
  });

  it.each([429, 502, 503, 504])("retries a GET on %s", async (status) => {
    const fetchFn = fetchSequence([status, 200]);
    const res = await engine().request({ endpoint: "x", method: "GET" });
    expect(fetchFn).toHaveBeenCalledTimes(2);
    expect(res.error).toBeNull();
  });

  it("does not retry a GET on 500 (not in the Python SDK's list)", async () => {
    const fetchFn = fetchSequence([500, 200]);
    const res = await engine().request({ endpoint: "x", method: "GET" });
    expect(fetchFn).toHaveBeenCalledTimes(1);
    expect(res.error?.code).toBe(500);
  });

  it("gives up after `total` retries and returns the last response", async () => {
    const fetchFn = fetchSequence([503, 503, 503, 503, 200]);
    const res = await engine().request({ endpoint: "x", method: "GET" });
    expect(fetchFn).toHaveBeenCalledTimes(4);
    expect(res.error?.code).toBe(503);
  });

  it("honors a numeric Retry-After header", async () => {
    vi.useFakeTimers();
    const fetchFn = fetchSequence([429, 200], { "retry-after": "2" });
    const pending = engine().request({ endpoint: "x", method: "GET" });
    await vi.advanceTimersByTimeAsync(1999);
    expect(fetchFn).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);
    expect(fetchFn).toHaveBeenCalledTimes(2);
    expect((await pending).error).toBeNull();
  });
});

describe("ApiEngine timeout and abort", () => {
  it("passes an AbortSignal to fetch even when the caller gave none", async () => {
    const fetchFn = fetchSequence([200]);
    await engine().request({ endpoint: "x", method: "GET" });
    const [, init] = fetchFn.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.signal).toBeInstanceOf(AbortSignal);
  });

  it("throws a 408 BriaException when the request exceeds requestTimeout", async () => {
    vi.useFakeTimers();
    const fetchFn = vi.fn(
      (_url: string, init: RequestInit) =>
        new Promise<Response>((_, reject) => {
          init.signal!.addEventListener("abort", () => reject(new Error("aborted")));
        }),
    );
    vi.stubGlobal("fetch", fetchFn);
    const pending = engine({ requestTimeout: 1 }).request({ endpoint: "x", method: "POST" });
    const failure = pending.catch((e: unknown) => e);
    await vi.advanceTimersByTimeAsync(1000);
    const err = await failure;
    expect(err).toBeInstanceOf(BriaException);
    expect((err as BriaException).code).toBe(408);
    expect(fetchFn).toHaveBeenCalledTimes(1);
  });

  it("rethrows the caller's own abort without retrying", async () => {
    const controller = new AbortController();
    const fetchFn = vi.fn(
      (_url: string, init: RequestInit) =>
        new Promise<Response>((_, reject) => {
          init.signal!.addEventListener("abort", () => reject(new Error("user abort")));
        }),
    );
    vi.stubGlobal("fetch", fetchFn);
    const pending = engine().request({ endpoint: "x", method: "GET", signal: controller.signal });
    controller.abort();
    await expect(pending).rejects.toThrow("user abort");
    expect(fetchFn).toHaveBeenCalledTimes(1);
  });

  it("rejects a non-positive requestTimeout", () => {
    expect(() => engine({ requestTimeout: 0 })).toThrow(/requestTimeout/);
  });
});
