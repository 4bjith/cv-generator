import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";
import { API_BASE_URL } from "@/lib/config";
import { normalizeApiError } from "@/lib/api/errors";
import { tokenStorage } from "@/lib/api/token-storage";
import { TokenRefreshResponse } from "@/types/auth";

interface CustomRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

interface QueuedPromise {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}

let isRefreshing = false;
let failedQueue: QueuedPromise[] = [];

const processQueue = (error: unknown, token: string | null = null): void => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Centralized Axios client instance.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================================
// Request Interceptor: Attach Bearer token
// ============================================================================
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = tokenStorage.getAccessToken();
    if (accessToken && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(normalizeApiError(error))
);

// ============================================================================
// Response Interceptor: 401 Handling & Single-Flight Refresh
// ============================================================================
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomRequestConfig | undefined;

    if (!originalRequest || !error.response) {
      return Promise.reject(normalizeApiError(error));
    }

    const is401 = error.response.status === 401;
    const url = originalRequest.url || "";
    const isAuthEndpoint =
      url.includes("/auth/login") ||
      url.includes("/auth/register") ||
      url.includes("/auth/refresh");

    // Only attempt refresh for 401s on protected endpoints that haven't been retried
    if (!is401 || originalRequest._retry || isAuthEndpoint) {
      return Promise.reject(normalizeApiError(error));
    }

    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      tokenStorage.clearTokens();
      return Promise.reject(normalizeApiError(error));
    }

    if (isRefreshing) {
      // Queue concurrent 401 requests while a refresh is in-flight
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        })
        .catch((err) => Promise.reject(normalizeApiError(err)));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Execute single-flight refresh request directly to avoid interceptor recursion
      const refreshResponse = await axios.post<TokenRefreshResponse>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        {
          headers: { "Content-Type": "application/json" },
          timeout: 10000,
        }
      );

      const { access_token, refresh_token: newRefreshToken } = refreshResponse.data;
      tokenStorage.setTokens({
        accessToken: access_token,
        refreshToken: newRefreshToken,
      });

      processQueue(null, access_token);
      originalRequest.headers.Authorization = `Bearer ${access_token}`;

      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      tokenStorage.clearTokens();
      return Promise.reject(normalizeApiError(refreshError));
    } finally {
      isRefreshing = false;
    }
  }
);
