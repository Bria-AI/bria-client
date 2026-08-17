import { describe, expect, it } from "vitest";

import { ApiEngine } from "../src/engine.js";

function engine(apiToken: string | null = "tok"): ApiEngine {
  return new ApiEngine({ baseUrl: "https://engine.prod.bria-api.com", apiToken });
}

describe("ApiEngine.prepareEndpoint", () => {
  const eng = engine();
  const base = "https://engine.prod.bria-api.com/v2";
  it.each([
    ["remove_background", `${base}/remove_background`],
    ["/remove_background/", `${base}/remove_background`],
    ["v2/remove_background", `${base}/remove_background`],
    ["/v2/remove_background", `${base}/remove_background`],
    ["status/req-123", `${base}/status/req-123`],
    ["video/upload", `${base}/video/upload`],
  ])("normalizes %s", (input, expected) => {
    expect(eng.prepareEndpoint(input)).toBe(expected);
  });
});

describe("ApiEngine.preparePayload", () => {
  it("drops top-level null/undefined and keeps falsy values", () => {
    const out = ApiEngine.preparePayload({ a: "x", b: null, c: undefined, d: false, e: 0, f: "" });
    expect(out).toEqual({ a: "x", d: false, e: 0, f: "" });
  });

  it("leaves nested objects untouched", () => {
    expect(ApiEngine.preparePayload({ x: 1, opts: { a: null, b: 1 }, drop: null })).toEqual({
      x: 1,
      opts: { a: null, b: 1 },
    });
  });

  it("returns null for null/undefined input", () => {
    expect(ApiEngine.preparePayload(null)).toBeNull();
    expect(ApiEngine.preparePayload(undefined)).toBeNull();
  });
});

describe("ApiEngine headers", () => {
  it("emits a js user-agent", () => {
    expect(engine().userAgentHeaders["User-Agent"]).toMatch(/^BriaSDK\/.+ \(js\)$/);
  });

  it("includes the api_token auth header", () => {
    expect(engine("secret").prepareHeaders().api_token).toBe("secret");
  });

  it("throws when no token is available", () => {
    expect(() => engine(null).prepareHeaders()).toThrow(/api_token is required/);
  });

  it("honors a per-call auth override", () => {
    const override = engine("default").checkAuthOverride("per-call");
    expect(engine("default").prepareHeaders(undefined, override).api_token).toBe("per-call");
  });
});
