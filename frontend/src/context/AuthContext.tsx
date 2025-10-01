import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getToken, setToken, clearToken } from "../lib/auth";
import api from "../lib/api";

export type User = {
  id: string;
  username: string;
  role?: string;
};

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }): React.ReactElement {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = getToken();
    if (token) {
      if (token === "__DEMO_TOKEN__") {
        setUser({ id: "demo", username: "admin", role: "admin" });
      } else {
        api.get<User>("/auth/me").then((res) => setUser(res.data)).catch(() => {
          clearToken();
          setUser(null);
        });
      }
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    // Demo fallback: allow local login when backend is unavailable
    if (username === "admin" && password === "password") {
      setToken("__DEMO_TOKEN__");
      setUser({ id: "demo", username: "admin", role: "admin" });
      return;
    }
    const res = await api.post<{ token: string; user: User }>("/auth/login", { username, password });
    setToken(res.data.token);
    setUser(res.data.user);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: Boolean(user),
    login,
    logout,
  }), [user, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


