import { BriaException } from "./errors.js";
import { Status, type BriaError, type BriaResult } from "./models.js";

/** A parsed Bria API response. Mirrors the Python `BriaResponse`. */
export class BriaResponse {
  readonly requestId: string;
  readonly status: Status;
  readonly error: BriaError | null;
  readonly result: BriaResult | null;
  readonly statusUrl: string | null;
  readonly headers: Record<string, string>;

  constructor(fields: {
    requestId?: string;
    status: Status;
    error?: BriaError | null;
    result?: BriaResult | null;
    statusUrl?: string | null;
    headers?: Record<string, string>;
  }) {
    this.requestId = fields.requestId ?? "unknown";
    this.status = fields.status;
    this.error = fields.error ?? null;
    this.result = fields.result ?? null;
    this.statusUrl = fields.statusUrl ?? null;
    this.headers = fields.headers ?? {};
  }

  /**
   * Build a response from a raw JSON body. Status is taken from an explicit `status` field if
   * present; otherwise derived: error -> ERROR, else result -> COMPLETED, else status_url ->
   * IN_PROGRESS, else UNKNOWN. (Matches Python `_prepare_model`.)
   */
  static fromBody(
    body: Record<string, unknown>,
    headers: Record<string, string> = {},
  ): BriaResponse {
    const error = (body.error as BriaError | undefined) ?? null;
    const result = (body.result as BriaResult | undefined) ?? null;
    const statusUrl = (body.status_url as string | undefined) ?? null;

    let derived = Status.UNKNOWN;
    if (error !== null) derived = Status.FAILED;
    else if (result !== null) derived = Status.COMPLETED;
    else if (statusUrl !== null) derived = Status.RUNNING;

    const status = (body.status as Status | undefined) ?? derived;

    return new BriaResponse({
      requestId: (body.request_id as string | undefined) ?? "unknown",
      status,
      error,
      result,
      statusUrl,
      headers,
    });
  }

  static fromError(error: BriaError, headers: Record<string, string> = {}): BriaResponse {
    return new BriaResponse({ status: Status.FAILED, error, headers });
  }

  /**
   * Build a response from a completed HTTP response. If the body is not a JSON object, or the
   * HTTP status is >= 400 with no `error` in the body, a `BriaError` is synthesized from the
   * status/reason/text. (Matches Python `from_http_response`.)
   */
  static fromHttpResponse(input: {
    statusCode: number;
    reasonPhrase: string;
    body: unknown;
    bodyText: string;
    headers?: Record<string, string>;
  }): BriaResponse {
    const headers = input.headers ?? {};
    let parsed: BriaResponse | null = null;
    if (input.body !== null && typeof input.body === "object" && !Array.isArray(input.body)) {
      parsed = BriaResponse.fromBody(input.body as Record<string, unknown>, headers);
    }
    if (parsed === null || (input.statusCode >= 400 && parsed.error === null)) {
      return BriaResponse.fromError(
        {
          code: input.statusCode,
          message: input.reasonPhrase || `HTTP ${input.statusCode}`,
          details: input.bodyText,
        },
        headers,
      );
    }
    return parsed;
  }

  /** True while the job is still running. */
  get inProgress(): boolean {
    return this.status === Status.RUNNING;
  }

  /** Throw a `BriaException` if this response carries an error; otherwise no-op. */
  raiseForStatus(): void {
    if (this.error !== null) {
      throw BriaException.fromError(this.error);
    }
  }
}
