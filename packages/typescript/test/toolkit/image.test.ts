import { describe, expect, it } from "vitest";

import { Image } from "../../src/toolkit/image.js";

describe("Image", () => {
  it("passes http URLs through untouched", () => {
    const url = "https://cdn.example.com/cat.png";
    expect(new Image(url).asBriaApiInput).toBe(url);
  });

  it("strips the data-URI prefix, keeping base64", () => {
    const b64 = Buffer.from("hello").toString("base64");
    expect(new Image(`data:image/png;base64,${b64}`).asBriaApiInput).toBe(b64);
  });

  it("passes a raw base64 string through", () => {
    const b64 = Buffer.from("some bytes here").toString("base64");
    expect(new Image(b64).asBriaApiInput).toBe(b64);
  });

  it("base64-encodes raw bytes", () => {
    const bytes = new Uint8Array([1, 2, 3, 4]);
    expect(new Image(bytes).asBriaApiInput).toBe(Buffer.from(bytes).toString("base64"));
  });

  it("throws a helpful error for a non-existent path", () => {
    expect(() => new Image("./does-not-exist.png")).toThrow(/Failed to process image/);
  });
});
