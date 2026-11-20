import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { api } from "@/lib/api";
import type { UserRead } from "@/types/auth";

interface AuthState {
  user: UserRead | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (accessToken: string, user: UserRead) => void;
  logout: () => void;
  setAuth: (accessToken: string, user: UserRead) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isLoading: false,
      isAuthenticated: false,

      login: (accessToken: string, user: UserRead) => {
        api.setToken(accessToken);
        set({
          user,
          accessToken,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        api.clearToken();
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setAuth: (accessToken: string, user: UserRead) => {
        api.setToken(accessToken);
        set({
          user,
          accessToken,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      clearAuth: () => {
        api.clearToken();
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: "careerpilot-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
