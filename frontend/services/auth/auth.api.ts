import { apiClient } from "@/lib/api/axios";
import {
  AuthResponse,
  LoginRequest,
  LogoutResponse,
  RegisterRequest,
  TokenRefreshResponse,
  User,
} from "@/types/auth";

/**
 * Authentication API Service.
 *
 * Encapsulates all authentication network operations with the FastAPI backend.
 */
export const authApi = {
  async register(payload: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/register", payload);
    return response.data;
  },

  async login(payload: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/login", payload);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  async refresh(refreshToken: string): Promise<TokenRefreshResponse> {
    const response = await apiClient.post<TokenRefreshResponse>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  async logout(): Promise<LogoutResponse> {
    const response = await apiClient.post<LogoutResponse>("/auth/logout");
    return response.data;
  },
};
