import { readFileSync } from "node:fs";

/**
 * A source that can be turned into a Bria API image input: an image URL, a data URI, a raw
 * base64 string, a local file path, or raw bytes.
 */
export type ImageSource = string | Buffer | Uint8Array;

/**
 * Normalizes an image into the string the Bria API expects — either an `http(s)` URL passed
 * through untouched, or a base64-encoded payload.
 *
 * The Python SDK also accepts PIL images and numpy arrays; those have no JS equivalent. Use a
 * URL, a data URI, a base64 string, a local path, or a Buffer/Uint8Array here. For a `Blob`,
 * use the async `Image.fromBlob(blob)`.
 *
 * @example
 * const img = new Image("./cat.png");
 * await client.run("remove_background", { image: img.asBriaApiInput });
 */
export class Image {
  private readonly value: string;

  constructor(source: ImageSource) {
    try {
      this.value = Image.process(source);
    } catch (e) {
      throw new Error(`Failed to process image: ${String(source)}`, { cause: e });
    }
  }

  /** The value to pass to the Bria API (a URL or base64 string). */
  get asBriaApiInput(): string {
    return this.value;
  }

  /** Build an `Image` from a `Blob` (browser File inputs, fetch bodies, etc.). */
  static async fromBlob(blob: Blob): Promise<Image> {
    const bytes = new Uint8Array(await blob.arrayBuffer());
    return new Image(bytes);
  }

  private static process(source: ImageSource): string {
    if (typeof source !== "string") {
      return Buffer.from(source).toString("base64");
    }
    if (source.startsWith("http")) {
      return source;
    }
    if (source.startsWith("data:") && source.includes(";base64,")) {
      return source.slice(source.indexOf(",") + 1);
    }
    if (Image.isBase64(source)) {
      return source;
    }
    // Otherwise treat it as a local file path.
    return readFileSync(source).toString("base64");
  }

  static isBase64(value: string): boolean {
    if (value.length === 0 || value.length % 4 !== 0) return false;
    if (!/^[A-Za-z0-9+/]*={0,2}$/.test(value)) return false;
    // Round-trip check: re-encoding the decoded bytes must reproduce the input.
    try {
      return Buffer.from(value, "base64").toString("base64") === value;
    } catch {
      return false;
    }
  }
}
