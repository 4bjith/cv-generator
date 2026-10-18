import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { authKeys } from "@/lib/query-keys";
import { tokenStorage } from "@/lib/api/token-storage";
import { authApi } from "@/services/auth/auth.api";
import {
  AuthResponse,
  LoginRequest,
  LogoutResponse,
  RegisterRequest,
  User,
} from "@/types/auth";

/**
 * Hook to retrieve and subscribe to the currently authenticated user's server state.
 */
export function useCurrentUser() {
  const [hasTokenState, setHasTokenState] = useState(false);

  // Listen to token changes across components/tabs and sync on mount
  useEffect(() => {
    setHasTokenState(tokenStorage.hasTokens());
    return tokenStorage.subscribe(() => {
      setHasTokenState(tokenStorage.hasTokens());
    });
  }, []);

  const query = useQuery<User, Error>({
    queryKey: authKeys.currentUser(),
    queryFn: async () => {
      return await authApi.getCurrentUser();
    },
    enabled: hasTokenState,
    staleTime: 60 * 1000,
  });

  const isAuthenticated = Boolean(hasTokenState && query.data && !query.isError);

  return {
    user: query.data ?? null,
    isLoading: query.isLoading && hasTokenState,
    isFetching: query.isFetching,
    isAuthenticated,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

/**
 * Hook for authenticating via login credentials.
 */
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation<AuthResponse, Error, LoginRequest>({
    mutationFn: async (credentials: LoginRequest) => {
      return await authApi.login(credentials);
    },
    onSuccess: (data) => {
      tokenStorage.setTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
      });
      queryClient.setQueryData(authKeys.currentUser(), data.user);
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}

/**
 * Hook for new candidate registration.
 */
export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation<AuthResponse, Error, RegisterRequest>({
    mutationFn: async (payload: RegisterRequest) => {
      return await authApi.register(payload);
    },
    onSuccess: (data) => {
      tokenStorage.setTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
      });
      queryClient.setQueryData(authKeys.currentUser(), data.user);
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}

/**
 * Hook for session logout.
 */
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation<LogoutResponse, Error, void>({
    mutationFn: async () => {
      try {
        return await authApi.logout();
      } catch {
        // If logout network request fails (e.g. server down), still proceed with client cleanup
        return { status: "ok", message: "Logged out locally" };
      }
    },
    onSettled: () => {
      tokenStorage.clearTokens();
      queryClient.setQueryData(authKeys.currentUser(), null);
      queryClient.clear();
    },
  });
}
