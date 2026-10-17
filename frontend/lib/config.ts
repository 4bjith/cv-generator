/**
 * Centralized application configuration.
 */

export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
