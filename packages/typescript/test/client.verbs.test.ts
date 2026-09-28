import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BriaClient } from "../src/client.js";
import { BriaException } from "../src/toolkit/errors.js";
import { Status } from "../src/toolkit/models.js";

afterEach(() => {
  vi.restoreAllMocks();
});

type Reply = { status?: number; body: unknown };
type Call = [string, RequestInit];

/** fetch stub replying with the given bodies in order; the last one repeats. */
function mockFetch(replies: Reply[]) {
  let n = 0;
  const fn = vi.fn(async () => {
    const r = replies[Math.min(n, replies.length - 1)]!;
    n++;
    return new Response(JSON.stringify(r.body), { status: r.status ?? 200 });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

function client(): BriaClient {
  return new BriaClient({
    apiToken: "secret",
    baseUrl: "https://api.test",
    retry: { total: 0, backoffFactor: 0 },
  });
}

function callAt(fetchFn: { mock: { calls: unknown[] } }, i: number): Call {
  return fetchFn.mock.calls[i] as Call;
}

function bodyOf(fetchFn: { mock: { calls: unknown[] } }, i = 0): Record<string, unknown> {
  return JSON.parse(callAt(fetchFn, i)[1].body as string);
}

describe("BriaClient.submit", () => {
  it("posts sync:false and the webhook_url", async () => {
    const fetchFn = mockFetch([{ body: { request_id: "r1", status_url: "https://s" } }]);
    const res = await client().submit("x", { a: 1 }, { webhookUrl: "https://hook" });
    expect(res.status).toBe(Status.RUNNING);
    expect(bodyOf(fetchFn)).toEqual({ a: 1, sync: false, webhook_url: "https://hook" });
  });

  it("omits webhook_url when not given", async () => {
    const fetchFn = mockFetch([{ body: { request_id: "r1", status_url: "https://s" } }]);
    await client().submit("x", { a: 1 });
    expect(bodyOf(fetchFn)).toEqual({ a: 1, sync: false });
  });

  it("rejects a payload that already sets sync", async () => {
    await expect(client().submit("x", { sync: false })).rejects.toThrow(/sync/);
  });
});

describe("BriaClient.get", () => {
  it("sends query params and no body", async () => {
    const fetchFn = mockFetch([{ body: { request_id: "r", result: {} } }]);
    await client().get("info", { params: { a: 1, b: null, c: "x" } });
    const [url, init] = callAt(fetchFn, 0);
    expect(url).toBe("https://api.test/v2/info?a=1&c=x");
    expect(init.method).toBe("GET");
    expect(init.body).toBeUndefined();
  });
});

describe("BriaClient.status", () => {
  it("GETs status/<id> and returns the Status", async () => {
    const fetchFn = mockFetch([{ body: { request_id: "r", status: "IN_PROGRESS" } }]);
    expect(await client().status("r")).toBe(Status.RUNNING);
    expect(callAt(fetchFn, 0)[0]).toBe("https://api.test/v2/status/r");
  });
});

describe("BriaClient.poll", () => {
  it("keeps polling while UNKNOWN or IN_PROGRESS, then returns the terminal response", async () => {
    const fetchFn = mockFetch([
      { body: { request_id: "r" } },
      { body: { request_id: "r", status: "IN_PROGRESS" } },
      { body: { request_id: "r", status: "COMPLETED", result: { ok: 1 } } },
    ]);
    const res = await client().poll("r", { interval: 0.001, timeout: 5 });
    expect(res.status).toBe(Status.COMPLETED);
    expect(fetchFn).toHaveBeenCalledTimes(3);
  });

  it("accepts a BriaResponse target", async () => {
    const fetchFn = mockFetch([{ body: { request_id: "r9", status: "COMPLETED", result: {} } }]);
    const submitted = await client().submit("x", {});
    await client().poll(submitted, { interval: 0.001, timeout: 5 });
    expect(callAt(fetchFn, 1)[0]).toBe("https://api.test/v2/status/r9");
  });

  it("throws on timeout", async () => {
    mockFetch([{ body: { request_id: "r", status: "IN_PROGRESS" } }]);
    await expect(client().poll("r", { interval: 0.005, timeout: 0.01 })).rejects.toThrow(/Timeout/);
  });

  it("raises for status by default on a failed job", async () => {
    mockFetch([{ body: { request_id: "r", error: { code: 422, message: "Bad", details: "d" } } }]);
    await expect(client().poll("r")).rejects.toBeInstanceOf(BriaException);
  });

  it.each([
    [0, 60],
    [Number.NaN, 60],
    [1, 0],
    [1, Number.POSITIVE_INFINITY],
  ])("rejects interval=%s timeout=%s", async (interval, timeout) => {
    await expect(client().poll("r", { interval, timeout })).rejects.toThrow(/positive seconds/);
  });
});

describe("BriaClient.upload", () => {
  const presign = {
    request_id: "u",
    result: {
      upload_url: "https://s3.test/bucket",
      upload_fields: { key: "k", policy: "p" },
      file_url: "https://cdn.test/k",
    },
  };

  function mockPresignThen(storage: Response) {
    const fn = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(presign), { status: 200 }))
      .mockResolvedValueOnce(storage);
    vi.stubGlobal("fetch", fn);
    return fn;
  }

  async function tempVideo(): Promise<string> {
    const dir = await mkdtemp(join(tmpdir(), "bria-"));
    const path = join(dir, "clip.mp4");
    await writeFile(path, "fake video");
    return path;
  }

  it("presigns, then POSTs the form with the policy fields, Content-Type and file", async () => {
    const fetchFn = mockPresignThen(new Response(null, { status: 204 }));

    const fileUrl = await client().upload(await tempVideo(), "video/mp4");

    expect(fileUrl).toBe("https://cdn.test/k");
    expect(bodyOf(fetchFn)).toEqual({ media_type: "video/mp4" });
    const [s3Url, s3Init] = callAt(fetchFn, 1);
    expect(s3Url).toBe("https://s3.test/bucket");
    const form = s3Init.body as FormData;
    expect(form.get("key")).toBe("k");
    expect(form.get("policy")).toBe("p");
    expect(form.get("Content-Type")).toBe("video/mp4");
    const file = form.get("file") as File;
    expect(file.name).toBe("clip.mp4");
    expect(file.type).toBe("video/mp4");
  });

  it("accepts raw bytes", async () => {
    const fetchFn = mockPresignThen(new Response(null, { status: 204 }));
    await client().upload(new Uint8Array([1, 2, 3]), "video/webm");
    const form = callAt(fetchFn, 1)[1].body as FormData;
    expect((form.get("file") as File).type).toBe("video/webm");
  });

  it("rejects a non-video media type before any request", async () => {
    const fetchFn = mockFetch([]);
    await expect(client().upload("x.png", "image/png")).rejects.toThrow(/image\/png/);
    expect(fetchFn).not.toHaveBeenCalled();
  });

  it("throws a BriaException with the storage status when the upload is refused", async () => {
    mockPresignThen(new Response("Access Denied", { status: 403 }));
    const failure = client().upload(await tempVideo(), "video/mp4");
    await expect(failure).rejects.toBeInstanceOf(BriaException);
    await expect(failure).rejects.toMatchObject({ code: 403, details: "Access Denied" });
  });

  it("surfaces a presign failure", async () => {
    mockFetch([{ status: 401, body: { error: { code: 401, message: "nope", details: "" } } }]);
    await expect(client().upload(await tempVideo(), "video/mp4")).rejects.toThrow("nope");
  });
});
