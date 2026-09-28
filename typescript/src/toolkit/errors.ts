import type { BriaError } from "./models.js";

/** Raised by `BriaResponse.raiseForStatus()` and on non-recoverable transport failures. */
export class BriaException extends Error {
  readonly code: number;
  readonly details: string | null;

  constructor(opts: { statusCode?: number; message?: string | null; details?: string | null }) {
    super(opts.message ?? "");
    this.name = "BriaException";
    this.code = opts.statusCode ?? 500;
    this.details = opts.details ?? null;
    // Preserve prototype chain when targeting older runtimes / bundlers.
    Object.setPrototypeOf(this, BriaException.prototype);
  }

  static fromError(error: BriaError): BriaException {
    return new BriaException({
      statusCode: error.code,
      message: error.message,
      details: error.details,
    });
  }
}
