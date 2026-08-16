import { describe, expect, it } from "vitest";

import { loadContract } from "../contract-loader.js";
import { ApiEngine, DEFAULT_RETRY } from "../../src/engine.js";
import { POLL_DEFAULTS } from "../../src/client.js";
import { BriaResponse } from "../../src/toolkit/response.js";
import { Status } from "../../src/toolkit/models.js";
import { verifyWebhookSignature } from "../../src/toolkit/webhook.js";

const constants = loadContract("constants.json");

function engine(baseUrl = constants.defaultBaseUrl): ApiEngine {
  return new ApiEngine({ baseUrl, apiToken: "tok" });
}

describe("contract: constants", () => {
  it("Status enum matches the contract", () => {
    expect(Status.UNKNOWN).toBe(constants.status.UNKNOWN);
    expect(Status.FAILED).toBe(constants.status.FAILED);
    expect(Status.COMPLETED).toBe(constants.status.COMPLETED);
    expect(Status.RUNNING).toBe(constants.status.RUNNING);
  });

  it("retry defaults match the contract", () => {
    expect(DEFAULT_RETRY.total).toBe(constants.retry.total);
    expect(DEFAULT_RETRY.backoffFactor).toBe(constants.retry.backoffFactor);
  });

  it("poll defaults match the contract", () => {
    expect(POLL_DEFAULTS.intervalSeconds).toBe(constants.poll.defaultIntervalSeconds);
    expect(POLL_DEFAULTS.timeoutSeconds).toBe(constants.poll.defaultTimeoutSeconds);
  });

  it("auth header name matches the contract", () => {
    const headers = engine().prepareHeaders();
    expect(headers[constants.authHeaderName]).toBe("tok");
  });
});

describe("contract: endpoint normalization", () => {
  const fx = loadContract("fixtures/endpoint-normalization.json");
  const eng = engine(fx.baseUrl);
  for (const c of fx.cases) {
    it(`normalizes ${JSON.stringify(c.input)}`, () => {
      expect(eng.prepareEndpoint(c.input)).toBe(c.expected);
    });
  }
});

describe("contract: payload null-stripping", () => {
  const fx = loadContract("fixtures/payload-null-stripping.json");
  for (const c of fx.cases) {
    it(c.name, () => {
      expect(ApiEngine.preparePayload(c.input)).toEqual(c.expected);
    });
  }
});

describe("contract: user-agent", () => {
  const fx = loadContract("fixtures/user-agent.json");
  const render = (version: string, lang: string) =>
    constants.userAgentTemplate.replace("{version}", version).replace("{lang}", lang);

  for (const c of fx.cases) {
    it(`renders ${c.lang} UA`, () => {
      expect(render(c.version, c.lang)).toBe(c.expected);
    });
  }

  it("engine emits a contract-shaped js user-agent", () => {
    const ua = engine().userAgentHeaders["User-Agent"];
    expect(ua).toMatch(/^BriaSDK\/.+ \(js\)$/);
  });
});

describe("contract: response parsing", () => {
  const fx = loadContract("fixtures/response-parsing.json");
  for (const c of fx.cases) {
    it(c.name, () => {
      const res = BriaResponse.fromBody(c.body);
      expect(res.requestId).toBe(c.expected.request_id);
      expect(res.status).toBe(c.expected.status);
      expect(res.inProgress).toBe(c.expected.inProgress);
      expect(res.error !== null).toBe(c.expected.hasError);
      expect(res.result !== null).toBe(c.expected.hasResult);
      if (c.expected.raiseForStatusThrows) {
        expect(() => res.raiseForStatus()).toThrow();
      } else {
        expect(() => res.raiseForStatus()).not.toThrow();
      }
    });
  }
});

describe("contract: http errors", () => {
  const fx = loadContract("fixtures/http-error.json");
  for (const c of fx.cases) {
    it(c.name, () => {
      const res = BriaResponse.fromHttpResponse({
        statusCode: c.statusCode,
        reasonPhrase: c.reasonPhrase,
        body: c.bodyText ? tryParse(c.bodyText) : null,
        bodyText: c.bodyText,
      });
      expect(res.error).toEqual(c.expectedError);
    });
  }
});

describe("contract: upload response", () => {
  const fx = loadContract("fixtures/upload-response.json");
  it("exposes presigned fields", () => {
    const res = BriaResponse.fromBody(fx.body);
    const result = res.result as Record<string, any>;
    expect(result.upload_url).toBe(fx.expected.uploadUrl);
    expect(result.file_url).toBe(fx.expected.fileUrl);
    expect(Object.keys(result.upload_fields).sort()).toEqual(
      [...fx.expected.uploadFieldKeys].sort(),
    );
  });
});

describe("contract: webhook verification", () => {
  const fx = loadContract("fixtures/webhook.json");
  for (const c of fx.cases) {
    it(c.name, () => {
      const ok = verifyWebhookSignature({
        payload: c.payload,
        webhookId: c.webhookId,
        timestamp: c.timestamp,
        signatureHeader: c.signatureHeader,
        apiToken: c.apiToken,
      });
      expect(ok).toBe(c.expected);
    });
  }
});

function tryParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}
