/** Terminal and in-flight states a Bria job can be in. Values match the Bria API wire format. */
export enum Status {
  UNKNOWN = "UNKNOWN",
  FAILED = "ERROR",
  COMPLETED = "COMPLETED",
  RUNNING = "IN_PROGRESS",
}

/** Structured error returned by the Bria API (or synthesized from a failing HTTP response). */
export interface BriaError {
  code: number;
  message: string;
  details: string;
}

/**
 * The `result` payload of a successful response. The Bria API returns different shapes per
 * endpoint, so this is an open record — access fields you expect for the endpoint you called.
 */
export type BriaResult = Record<string, unknown>;
