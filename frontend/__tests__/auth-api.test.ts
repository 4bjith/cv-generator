import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { authApi } from "@/services/auth/auth.api";

describe("Auth API Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("calls POST /auth/register with payload", async () => {
    const mockUser = {
      id: "u-1",
      email: "new@example.com",
      full_name: "New Candidate",
      is_active: true,
      created_at: "2026-10-05T00:00:00Z",
    };
    const mockResponse = {
      data: {
        access_token: "acc_1",
        refresh_token: "ref_1",
        token_type: "bearer",
        expires_in: 3600,
        user: mockUser,
      },
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce(mockResponse);

    const result = await authApi.register({
      email: "new@example.com",
      password: "Password123!",
      full_name: "New Candidate",
    });

    expect(postSpy).toHaveBeenCalledWith("/auth/register", {
      email: "new@example.com",
      password: "Password123!",
      full_name: "New Candidate",
    });
    expect(result.access_token).toBe("acc_1");
    expect(result.user.email).toBe("new@example.com");
  });

  it("calls POST /auth/login with credentials", async () => {
    const mockResponse = {
      data: {
        access_token: "acc_2",
        refresh_token: "ref_2",
        token_type: "bearer",
        expires_in: 3600,
        user: {
          id: "u-2",
          email: "login@example.com",
          full_name: "Login User",
          is_active: true,
          created_at: "2026-10-05T00:00:00Z",
        },
      },
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce(mockResponse);

    const result = await authApi.login({
      email: "login@example.com",
      password: "Password123!",
    });

    expect(postSpy).toHaveBeenCalledWith("/auth/login", {
      email: "login@example.com",
      password: "Password123!",
    });
    expect(result.access_token).toBe("acc_2");
  });

  it("calls GET /auth/me for current profile", async () => {
    const mockUser = {
      id: "u-3",
      email: "me@example.com",
      full_name: "Me User",
      is_active: true,
      created_at: "2026-10-05T00:00:00Z",
    };
    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockUser });

    const result = await authApi.getCurrentUser();
    expect(getSpy).toHaveBeenCalledWith("/auth/me");
    expect(result.id).toBe("u-3");
    expect(result.email).toBe("me@example.com");
  });

  it("calls POST /auth/logout", async () => {
    const postSpy = vi
      .spyOn(apiClient, "post")
      .mockResolvedValueOnce({ data: { status: "ok", message: "Logged out" } });

    const result = await authApi.logout();
    expect(postSpy).toHaveBeenCalledWith("/auth/logout");
    expect(result.status).toBe("ok");
  });
});
