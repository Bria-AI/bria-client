import { describe, expect, it } from "vitest";

import { BriaResponse } from "../../src/toolkit/response.js";
import { Status } from "../../src/toolkit/models.js";

describe("BriaResponse.fromBody status derivation", () => {
  it("COMPLETED when a result is present", () => {
    const res = BriaResponse.fromBody({ request_id: "r", result: { image_url: "x" } });
    expect(res.status).toBe(Status.COMPLETED);
    expect(res.inProgress).toBe(false);
  });

  it("IN_PROGRESS when only a status_url is present", () => {
    const res = BriaResponse.fromBody({ request_id: "r", status_url: "https://…/status/r" });
    expect(res.status).toBe(Status.RUNNING);
    expect(res.inProgress).toBe(true);
  });

  it("ERROR when an error is present, and raiseForStatus throws", () => {
    const res = BriaResponse.fromBody({
      request_id: "r",
      error: { code: 422, message: "Bad", details: "nope" },
    });
    expect(res.status).toBe(Status.FAILED);
    expect(() => res.raiseForStatus()).toThrow("Bad");
  });

  it("UNKNOWN when empty", () => {
    expect(BriaResponse.fromBody({ request_id: "r" }).status).toBe(Status.UNKNOWN);
  });

  it("an explicit status wins over derivation", () => {
    const res = BriaResponse.fromBody({
      request_id: "r",
      status: Status.COMPLETED,
      status_url: "https://…",
    });
    expect(res.status).toBe(Status.COMPLETED);
  });
});

describe("BriaResponse.fromHttpResponse", () => {
  it("synthesizes an error for a 4xx/5xx body with no error field", () => {
    const res = BriaResponse.fromHttpResponse({
      statusCode: 500,
      reasonPhrase: "Internal Server Error",
      body: null,
      bodyText: "boom",
    });
    expect(res.error).toEqual({ code: 500, message: "Internal Server Error", details: "boom" });
  });

  it("falls back to `HTTP {code}` when there is no reason phrase", () => {
    const res = BriaResponse.fromHttpResponse({
      statusCode: 404,
      reasonPhrase: "",
      body: null,
      bodyText: "",
    });
    expect(res.error?.message).toBe("HTTP 404");
  });

  it("exposes presigned upload fields from a result body", () => {
    const res = BriaResponse.fromHttpResponse({
      statusCode: 200,
      reasonPhrase: "OK",
      body: { request_id: "u", result: { upload_url: "https://s3", file_url: "https://cdn" } },
      bodyText: "",
    });
    const result = res.result as Record<string, unknown>;
    expect(result.upload_url).toBe("https://s3");
    expect(result.file_url).toBe("https://cdn");
  });
});
