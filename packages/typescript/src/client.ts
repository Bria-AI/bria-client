import { basename } from "node:path";
import { readFile } from "node:fs/promises";

import { ApiEngine, type RetryConfig } from "./engine.js";
import { resolveSettings } from "./settings.js";
import { BriaResponse } from "./toolkit/response.js";
import { BriaException } from "./toolkit/errors.js";
import { Status } from "./toolkit/models.js";

/** Options for constructing a {@link BriaClient}. */
export interface BriaClientOptions {
  baseUrl?: string | null;
  apiToken?: string | null;
  defaultHeaders?: Record<string, string>;
  retry?: RetryConfig;
}

/** Per-call options shared by most methods. */
interface CallOptions {
  headers?: Record<string, string>;
  raiseForStatus?: boolean;
  /** Override the client's API token for this call only. */
  apiToken?: string;
  signal?: AbortSignal;
}

/** A file source accepted by {@link BriaClient.upload}. */
export type UploadSource = string | Buffer | Uint8Array | Blob;

/** Default poll cadence (seconds). Kept in one place so it can be asserted against the contract. */
export const POLL_DEFAULTS = { intervalSeconds: 1, timeoutSeconds: 60 } as const;

/**
 * Asynchronous client for the Bria Engine API.
 *
 * Unlike the Python SDK there is no separate sync client — JavaScript HTTP is always async, so
 * every method returns a `Promise`. `run` vs `submit` still map to the API's `sync` flag
 * (`run` = synchronous job, `submit` = asynchronous job you poll or receive via webhook).
 *
 * @example
 * const client = new BriaClient({ apiToken: process.env.BRIA_API_TOKEN });
 * const res = await client.run("remove_background", { image_url: "https://..." }, { raiseForStatus: true });
 * console.log(res.result);
 */
export class BriaClient {
  private readonly engine: ApiEngine;

  constructor(options: BriaClientOptions = {}) {
    const settings = resolveSettings({ baseUrl: options.baseUrl, apiToken: options.apiToken });
    this.engine = new ApiEngine({
      baseUrl: settings.baseUrl,
      apiToken: settings.apiToken,
      defaultHeaders: options.defaultHeaders,
      retry: options.retry,
    });
  }

  /** Run a synchronous job (`sync: true`). Resolves once the job is complete. */
  async run(
    endpoint: string,
    payload: Record<string, unknown>,
    options: CallOptions = {},
  ): Promise<BriaResponse> {
    assertNoSyncFlag(payload, "run");
    const response = await this.engine.request({
      endpoint,
      method: "POST",
      payload: { ...payload, sync: true },
      headers: options.headers,
      authOverride: this.engine.checkAuthOverride(options.apiToken),
      signal: options.signal,
    });
    if (options.raiseForStatus) response.raiseForStatus();
    return response;
  }

  /**
   * Submit an asynchronous job (`sync: false`). Returns immediately with a `request_id` to
   * poll, or provide `webhookUrl` to receive a signed callback on completion.
   */
  async submit(
    endpoint: string,
    payload: Record<string, unknown>,
    options: CallOptions & { webhookUrl?: string } = {},
  ): Promise<BriaResponse> {
    assertNoSyncFlag(payload, "submit");
    const merged: Record<string, unknown> = { ...payload, sync: false };
    if (options.webhookUrl !== undefined) merged.webhook_url = options.webhookUrl;
    const response = await this.engine.request({
      endpoint,
      method: "POST",
      payload: merged,
      headers: options.headers,
      authOverride: this.engine.checkAuthOverride(options.apiToken),
      signal: options.signal,
    });
    if (options.raiseForStatus) response.raiseForStatus();
    return response;
  }

  /** Perform a GET request against an endpoint. */
  async get(
    endpoint: string,
    options: CallOptions & { params?: Record<string, unknown> } = {},
  ): Promise<BriaResponse> {
    const response = await this.engine.request({
      endpoint,
      method: "GET",
      params: options.params,
      headers: options.headers,
      authOverride: this.engine.checkAuthOverride(options.apiToken),
      signal: options.signal,
    });
    if (options.raiseForStatus) response.raiseForStatus();
    return response;
  }

  /**
   * Upload a local file (or bytes) to Bria storage and return a `file_url` usable as input to
   * later API calls. The URL is valid for ~1 day.
   */
  async upload(
    source: UploadSource,
    options: { mediaType?: string; headers?: Record<string, string>; apiToken?: string } = {},
  ): Promise<string> {
    const { mediaType } = options;
    if (mediaType !== undefined && !mediaType.startsWith("video/")) {
      throw new Error(`Upload not yet supported for media type: ${mediaType}`);
    }

    const response = await this.engine.request({
      endpoint: "video/upload",
      method: "POST",
      payload: { media_type: mediaType },
      headers: options.headers,
      authOverride: this.engine.checkAuthOverride(options.apiToken),
    });
    response.raiseForStatus();

    const result = response.result;
    if (!result) throw new Error("Upload failed: response is missing a result");
    const uploadUrl = result.upload_url as string;
    const uploadFields = (result.upload_fields as Record<string, string> | undefined) ?? {};
    const fileUrl = result.file_url as string;

    const { blob, filename } = await toFilePart(source, mediaType);
    const form = new FormData();
    for (const [key, value] of Object.entries(uploadFields)) form.append(key, value);
    form.append("file", blob, filename);

    const putRes = await fetch(uploadUrl, { method: "POST", body: form });
    if (putRes.status !== 204) {
      throw new BriaException({
        statusCode: putRes.status,
        message: "Upload failed",
        details: await putRes.text(),
      });
    }
    return fileUrl;
  }

  /** Fetch the current {@link Status} of a submitted job. */
  async status(requestId: string, options: CallOptions = {}): Promise<Status> {
    const response = await this.engine.request({
      endpoint: `status/${requestId}`,
      method: "GET",
      headers: options.headers,
      authOverride: this.engine.checkAuthOverride(options.apiToken),
      signal: options.signal,
    });
    return response.status;
  }

  /**
   * Poll a submitted job until it reaches a terminal state.
   *
   * @param target    A `request_id` string or a {@link BriaResponse} from `submit`.
   * @param options   `interval`/`timeout` in seconds (defaults 1/60). `raiseForStatus` defaults true.
   */
  async poll(
    target: string | BriaResponse,
    options: CallOptions & { interval?: number; timeout?: number } = {},
  ): Promise<BriaResponse> {
    const requestId = typeof target === "string" ? target : target.requestId;
    const interval = options.interval ?? POLL_DEFAULTS.intervalSeconds;
    const timeout = options.timeout ?? POLL_DEFAULTS.timeoutSeconds;
    const raiseForStatus = options.raiseForStatus ?? true;

    const call = () =>
      this.engine.request({
        endpoint: `status/${requestId}`,
        method: "GET",
        headers: options.headers,
        authOverride: this.engine.checkAuthOverride(options.apiToken),
        signal: options.signal,
      });

    let response = await call();
    const start = Date.now();
    while (response.inProgress) {
      await sleep(interval * 1000);
      response = await call();
      if ((Date.now() - start) / 1000 >= timeout) {
        throw new Error("Timeout reached while waiting for status request");
      }
    }
    if (raiseForStatus) response.raiseForStatus();
    return response;
  }
}

function assertNoSyncFlag(payload: Record<string, unknown>, method: "run" | "submit"): void {
  if ("sync" in payload) {
    const other = method === "run" ? "submit" : "run";
    throw new Error(`.${method}() always sets sync itself (to control it call .${other}())`);
  }
}

async function toFilePart(
  source: UploadSource,
  mediaType?: string,
): Promise<{ blob: Blob; filename: string }> {
  if (typeof source === "string") {
    const buf = await readFile(source);
    return {
      blob: new Blob([buf], mediaType ? { type: mediaType } : {}),
      filename: basename(source),
    };
  }
  if (source instanceof Blob) {
    return { blob: source, filename: "file" };
  }
  return { blob: new Blob([source], mediaType ? { type: mediaType } : {}), filename: "file" };
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
