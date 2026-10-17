import { AxiosError } from "axios";
import { ApiErrorDetail, ApiErrorResponse } from "@/types/auth";

/**
 * Standardized client-side API error class.
 */
export class ApiClientError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly requestId?: string;
  public readonly details?: ApiErrorDetail[];

  constructor(params: {
    message: string;
    code?: string;
    status?: number;
    requestId?: string;
    details?: ApiErrorDetail[];
  }) {
    super(params.message);
    this.name = "ApiClientError";
    this.code = params.code || "UNKNOWN_ERROR";
    this.status = params.status || 500;
    this.requestId = params.requestId;
    this.details = params.details;
    Object.setPrototypeOf(this, ApiClientError.prototype);
  }
}

/**
 * Maps standard API error codes to human-friendly UX messages.
 */
export function toUserFriendlyMessage(error: unknown): string {
  if (error instanceof ApiClientError) {
    switch (error.code) {
      case "EMAIL_ALREADY_EXISTS":
        return "An account with this email address already exists. Please sign in instead.";
      case "INVALID_CREDENTIALS":
        return "Incorrect email address or password. Please try again.";
      case "REVOKED_REFRESH_TOKEN":
      case "INVALID_REFRESH_SESSION":
        return "Your session has expired. Please sign in again.";
      case "AUTHENTICATION_REQUIRED":
        return "Please sign in to access your workspace.";
      case "VALIDATION_ERROR":
        if (error.details && error.details.length > 0) {
          const firstDetail = error.details[0];
          return firstDetail.msg || firstDetail.message || error.message;
        }
        return error.message || "Please verify your input fields.";
      case "INTERNAL_ERROR":
      case "SERVICE_UNAVAILABLE":
        return "The server is temporarily unavailable. Please try again in a moment.";
      default:
        return error.message || "An unexpected error occurred. Please try again.";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred. Please try again.";
}

/**
 * Normalizes any error (AxiosError, Network Error, etc.) into an ApiClientError instance.
 */
export function normalizeApiError(error: unknown): ApiClientError {
  if (error instanceof ApiClientError) {
    return error;
  }

  if (error && typeof error === "object" && "isAxiosError" in error) {
    const axiosError = error as AxiosError<ApiErrorResponse>;
    const status = axiosError.response?.status || 500;
    const responseData = axiosError.response?.data;
    const requestId =
      responseData?.error?.request_id ||
      (axiosError.response?.headers?.["x-request-id"] as string | undefined);

    if (responseData && responseData.error) {
      return new ApiClientError({
        code: responseData.error.code,
        message: responseData.error.message,
        status,
        requestId,
        details: responseData.error.details,
      });
    }

    if (axiosError.code === "ECONNABORTED" || axiosError.message.includes("timeout")) {
      return new ApiClientError({
        code: "TIMEOUT",
        message: "The request timed out. Please check your network connection.",
        status: 408,
      });
    }

    if (!axiosError.response) {
      return new ApiClientError({
        code: "NETWORK_ERROR",
        message: "Unable to connect to the server. Please verify the backend is running.",
        status: 503,
      });
    }

    return new ApiClientError({
      code: `HTTP_${status}`,
      message: axiosError.message || `Request failed with status ${status}`,
      status,
      requestId,
    });
  }

  if (error instanceof Error) {
    return new ApiClientError({
      code: "CLIENT_ERROR",
      message: error.message,
      status: 500,
    });
  }

  return new ApiClientError({
    code: "UNKNOWN_ERROR",
    message: "An unknown error occurred.",
    status: 500,
  });
}
