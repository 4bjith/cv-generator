import { describe, it, expect, beforeEach } from "vitest";
import { tokenStorage } from "@/lib/api/token-storage";

describe("Token Storage", () => {
  // In-memory mock localStorage for Node test environment
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
  });

  it("stores and retrieves access and refresh tokens", () => {
    tokenStorage.setTokens({
      accessToken: "access_token_123",
      refreshToken: "refresh_token_456",
    });

    expect(tokenStorage.getAccessToken()).toBe("access_token_123");
    expect(tokenStorage.getRefreshToken()).toBe("refresh_token_456");
    expect(tokenStorage.hasTokens()).toBe(true);
  });

  it("clears stored tokens cleanly", () => {
    tokenStorage.setTokens({
      accessToken: "access_token_abc",
      refreshToken: "refresh_token_xyz",
    });

    tokenStorage.clearTokens();
    expect(tokenStorage.getAccessToken()).toBeNull();
    expect(tokenStorage.getRefreshToken()).toBeNull();
    expect(tokenStorage.hasTokens()).toBe(false);
  });

  it("notifies subscribers when tokens change", () => {
    let callCount = 0;
    const unsubscribe = tokenStorage.subscribe(() => {
      callCount += 1;
    });

    tokenStorage.setAccessToken("new_token");
    expect(callCount).toBe(1);

    tokenStorage.clearTokens();
    expect(callCount).toBe(2);

    unsubscribe();
    tokenStorage.setAccessToken("another_token");
    expect(callCount).toBe(2);
  });
});
