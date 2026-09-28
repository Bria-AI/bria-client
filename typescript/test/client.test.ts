import { afterEach, describe, expect, it, vi } from "vitest";

import { BriaClient } from "../src/client.js";
import { Status } from "../src/toolkit/models.js";

afterEach(() => {
  vi.restoreAllMocks();
});

function mockFetchOnce(status: number, body: unknown): ReturnType<typeof vi.fn> {
  const fn = vi.fn(
    async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: { "content-type": "application/json" },
      }),
  );
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("BriaClient.run", () => {
  it("posts to the /v2/ endpoint with sync:true and the auth header", async () => {
    const fetchFn = mockFetchOnce(200, { request_id: "r1", result: { image_url: "x" } });
    const client = new BriaClient({ apiToken: "secret", baseUrl: "https://api.test" });

    const res = await client.run("remove_background", { image_url: "https://in" });

    expect(res.status).toBe(Status.COMPLETED);
    expect(fetchFn).toHaveBeenCalledOnce();
    const [url, init] = fetchFn.mock.calls[0]!;
    expect(url).toBe("https://api.test/v2/remove_background");
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>).api_token).toBe("secret");
    expect(JSON.parse(init.body as string)).toEqual({ image_url: "https://in", sync: true });
  });

  it("rejects a payload that already sets sync", async () => {
    const client = new BriaClient({ apiToken: "secret" });
    await expect(client.run("x", { sync: true })).rejects.toThrow(/sync/);
  });

  it("raiseForStatus surfaces API errors", async () => {
    mockFetchOnce(422, { error: { code: 422, message: "Bad", details: "nope" } });
    const client = new BriaClient({ apiToken: "secret" });
    await expect(client.run("x", {}, { raiseForStatus: true })).rejects.toThrow("Bad");
  });
});
