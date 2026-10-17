/**
 * Centralized Token Storage.
 *
 * Provides a clean abstraction for accessing and persisting JWT access and refresh tokens.
 * Tokens are never logged, never exposed in URLs, and centralized in this module.
 */

const ACCESS_TOKEN_KEY = "ai_cv_access_token";
const REFRESH_TOKEN_KEY = "ai_cv_refresh_token";

type TokenChangeListener = () => void;
const listeners = new Set<TokenChangeListener>();

function notifyListeners(): void {
  listeners.forEach((listener) => {
    try {
      listener();
    } catch {
      // Ignore listener errors
    }
  });
}

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    try {
      return localStorage.getItem(ACCESS_TOKEN_KEY);
    } catch {
      return null;
    }
  },

  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    try {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    } catch {
      return null;
    }
  },

  setTokens(tokens: { accessToken: string; refreshToken: string }): void {
    if (typeof window === "undefined") return;
    try {
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
      notifyListeners();
    } catch {
      // Storage quota or disabled storage
    }
  },

  setAccessToken(accessToken: string): void {
    if (typeof window === "undefined") return;
    try {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      notifyListeners();
    } catch {
      // Storage quota or disabled storage
    }
  },

  clearTokens(): void {
    if (typeof window === "undefined") return;
    try {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      notifyListeners();
    } catch {
      // Storage error
    }
  },

  hasTokens(): boolean {
    return Boolean(this.getAccessToken() || this.getRefreshToken());
  },

  subscribe(listener: TokenChangeListener): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};
