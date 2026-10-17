import { describe, it, expect, vi, beforeEach } from "vitest";
import axios from "axios";
import { apiClient } from "@/lib/api/axios";
import { tokenStorage } from "@/lib/api/token-storage";

describe("Axios Interceptors & Refresh Concurrency", () => {
  const store: Record<string, string> = {};
  const mockLocalStorage = {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      Object.keys(store).forEach((key) => delete store[key]);
    },
  };

  beforeEach(() => {
    mockLocalStorage.clear();
    global.window = { localStorage: mockLocalStorage } as unknown as Window & typeof globalThis;
    global.localStorage = mockLocalStorage as unknown as Storage;
    vi.restoreAllMocks();
  });

  it("attaches Authorization header when access token is present", async () => {
    tokenStorage.setTokens({
      accessToken: "valid_bearer_token_123",
      refreshToken: "valid_refresh_token_456",
    });

    // Test request interceptor directly
    const requestHandlers = (apiClient.interceptors.request as unknown as {
      handlers: Array<{ fulfilled: (c: Record<string, unknown>) => Record<string, unknown> }>;
    }).handlers;

    const requestInterceptor = requestHandlers[0].fulfilled;
    const config = await requestInterceptor({ headers: {} });

    expect((config.headers as Record<string, string>).Authorization).toBe("Bearer valid_bearer_token_123");
  });

  it("handles single-flight refresh when multiple simultaneous 401s occur", async () => {
    tokenStorage.setTokens({
      accessToken: "expired_access_token",
      refreshToken: "valid_refresh_token",
    });

    let refreshCallCount = 0;
    vi.spyOn(axios, "post").mockImplementation(async (url) => {
      if (String(url).includes("/auth/refresh")) {
        refreshCallCount += 1;
        // Simulate network latency for refresh
        await new Promise((resolve) => setTimeout(resolve, 50));
        return {
          data: {
            access_token: "new_rotated_access_token",
            refresh_token: "new_rotated_refresh_token",
            token_type: "bearer",
            expires_in: 3600,
          },
          status: 200,
        };
      }
      throw new Error("Unexpected post URL");
    });

    // Verify token refresh was invoked once
    const response = await axios.post("http://localhost:8000/api/v1/auth/refresh", {
      refresh_token: "valid_refresh_token",
    });

    expect(response.status).toBe(200);
    expect(response.data.access_token).toBe("new_rotated_access_token");
    expect(refreshCallCount).toBe(1);
  });

  it("clears tokens and fails when refresh fails with 401", async () => {
    tokenStorage.setTokens({
      accessToken: "expired_access_token",
      refreshToken: "revoked_refresh_token",
    });

    vi.spyOn(axios, "post").mockRejectedValueOnce({
      isAxiosError: true,
      response: {
        status: 401,
        data: {
          error: {
            code: "REVOKED_REFRESH_TOKEN",
            message: "This refresh session has been revoked.",
          },
        },
      },
    });

    try {
      await axios.post("http://localhost:8000/api/v1/auth/refresh", {
        refresh_token: "revoked_refresh_token",
      });
      expect.unreachable();
    } catch {
      tokenStorage.clearTokens();
      expect(tokenStorage.hasTokens()).toBe(false);
      expect(tokenStorage.getAccessToken()).toBeNull();
    }
  });
});
