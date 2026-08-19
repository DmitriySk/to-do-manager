import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

import { fetchMe, logout as apiLogout, loginUrl } from "../api/auth";
import { ApiError } from "../api/client";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (provider: "google" | "github") => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchMe()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch((err) => {
        if (!cancelled && !(err instanceof ApiError && err.status === 401)) {
          console.error("Failed to load current user", err);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback((provider: "google" | "github") => {
    // Full page redirect is required: OAuth + cookie session can't be driven via fetch/XHR.
    window.location.href = loginUrl(provider);
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
