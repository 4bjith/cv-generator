import { describe, it, expect } from "vitest";
import { ApiClientError, normalizeApiError, toUserFriendlyMessage } from "@/lib/api/errors";

describe("API Error Normalization", () => {
  it("creates ApiClientError with code, status, requestId, and details", () => {
    const error = new ApiClientError({
      code: "VALIDATION_ERROR",
      message: "Validation failed",
      status: 422,
      requestId: "req_test_123",
      details: [{ field: "email", message: "Invalid email" }],
    });

    expect(error.code).toBe("VALIDATION_ERROR");
    expect(error.status).toBe(422);
    expect(error.requestId).toBe("req_test_123");
    expect(error.details).toHaveLength(1);
    expect(error.message).toBe("Validation failed");
  });

  it("normalizes AxiosError with standard backend error response payload", () => {
    const mockAxiosError = {
      isAxiosError: true,
      response: {
        status: 409,
        headers: { "x-request-id": "req_conflict_456" },
        data: {
          error: {
            code: "EMAIL_ALREADY_EXISTS",
            message: "A user with email test@example.com already exists.",
            request_id: "req_conflict_456",
          },
        },
      },
    };

    const normalized = normalizeApiError(mockAxiosError);
    expect(normalized).toBeInstanceOf(ApiClientError);
    expect(normalized.code).toBe("EMAIL_ALREADY_EXISTS");
    expect(normalized.status).toBe(409);
    expect(normalized.requestId).toBe("req_conflict_456");
  });

  it("maps error codes to friendly UX messages", () => {
    const conflictError = new ApiClientError({
      code: "EMAIL_ALREADY_EXISTS",
      message: "Internal conflict",
      status: 409,
    });
    expect(toUserFriendlyMessage(conflictError)).toContain("already exists");

    const credsError = new ApiClientError({
      code: "INVALID_CREDENTIALS",
      message: "Wrong pass",
      status: 401,
    });
    expect(toUserFriendlyMessage(credsError)).toContain("Incorrect email address or password");

    const sessionError = new ApiClientError({
      code: "REVOKED_REFRESH_TOKEN",
      message: "Token revoked",
      status: 401,
    });
    expect(toUserFriendlyMessage(sessionError)).toContain("session has expired");
  });
});
