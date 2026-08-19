import { API_BASE_URL, apiClient } from "./client";
import type { User } from "../types";

export function loginUrl(provider: "google" | "github"): string {
  return `${API_BASE_URL}/auth/login/${provider}`;
}

export const fetchMe = () => apiClient.get<User>("/auth/me");

export const logout = () => apiClient.post<{ ok: boolean }>("/auth/logout");
