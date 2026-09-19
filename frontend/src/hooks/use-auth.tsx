'use client';

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';
import { api, setTokens, clearTokens, getTokens } from '@/lib/api-client';
import type { User, AuthResponse } from '@/types/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string, phone?: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    const { access } = getTokens();
    if (!access) {
      setIsLoading(false);
      return;
    }

    try {
      const userData = await api.get<User>('/auth/me');
      setUser(userData);
    } catch {
      clearTokens();
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email: string, password: string) => {
    const response = await api.post<AuthResponse>('/auth/login', { email, password });
    setTokens(response.tokens.access_token, response.tokens.refresh_token);
    setUser(response.user);
  };

  const signup = async (email: string, password: string, fullName: string, phone?: string) => {
    const response = await api.post<AuthResponse>('/auth/signup', {
      email,
      password,
      full_name: fullName,
      phone: phone || null,
    });
    setTokens(response.tokens.access_token, response.tokens.refresh_token);
    setUser(response.user);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    window.location.href = '/login';
  };

  const updateUser = (data: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...data });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
