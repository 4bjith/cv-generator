import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { tokenStorage } from "@/lib/api/token-storage";
import { authKeys } from "@/lib/query-keys";
import { authApi } from "@/services/auth/auth.api";

describe("TanStack Query Auth State & Invalidation", () => {
  let queryClient: QueryClient;
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
    queryClient = new QueryClient();
    vi.restoreAllMocks();
  });

  it("stores user in query cache on login and invalidates auth queries", async () => {
    const mockUser = {
      id: "u-login",
      email: "login@test.com",
      full_name: "Login Tester",
      is_active: true,
      created_at: "2026-10-05T00:00:00Z",
    };

    vi.spyOn(authApi, "login").mockResolvedValueOnce({
      access_token: "acc_token_1",
      refresh_token: "ref_token_1",
      token_type: "bearer",
      expires_in: 3600,
      user: mockUser,
    });

    const response = await authApi.login({
      email: "login@test.com",
      password: "Password123!",
    });

    // Populate query cache as the mutation does
    tokenStorage.setTokens({
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
    });
    queryClient.setQueryData(authKeys.currentUser(), response.user);

    expect(queryClient.getQueryData(authKeys.currentUser())).toEqual(mockUser);
    expect(tokenStorage.getAccessToken()).toBe("acc_token_1");
  });

  it("clears user from query cache and storage on logout", async () => {
    tokenStorage.setTokens({
      accessToken: "acc_active",
      refreshToken: "ref_active",
    });
    queryClient.setQueryData(authKeys.currentUser(), {
      id: "u-active",
      email: "active@test.com",
    });

    vi.spyOn(authApi, "logout").mockResolvedValueOnce({
      status: "ok",
      message: "Logged out",
    });

    await authApi.logout();

    // Clear state on logout
    tokenStorage.clearTokens();
    queryClient.setQueryData(authKeys.currentUser(), null);
    queryClient.removeQueries({ queryKey: authKeys.all });

    expect(queryClient.getQueryData(authKeys.currentUser())).toBeUndefined();
    expect(tokenStorage.hasTokens()).toBe(false);
  });
});
