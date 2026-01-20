'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Profile } from '@/types';

interface AuthState {
    user: User | null;
    profile: Profile | null;
    isAuthenticated: boolean;
    setUser: (user: User | null) => void;
    setProfile: (profile: Profile | null) => void;
    login: (user: User, accessToken: string, refreshToken: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            profile: null,
            isAuthenticated: false,

            setUser: (user) => set({ user, isAuthenticated: !!user }),

            setProfile: (profile) => set({ profile }),

            login: (user, accessToken, refreshToken) => {
                localStorage.setItem('access_token', accessToken);
                localStorage.setItem('refresh_token', refreshToken);
                set({ user, isAuthenticated: true });
            },

            logout: () => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                set({ user: null, profile: null, isAuthenticated: false });
            },
        }),
        {
            name: 'jarvis-auth',
            partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
        }
    )
);

// UI Store for global UI state
interface UIState {
    sidebarOpen: boolean;
    theme: 'light' | 'dark';
    toggleSidebar: () => void;
    setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIState>()(
    persist(
        (set) => ({
            sidebarOpen: true,
            theme: 'dark',

            toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

            setTheme: (theme) => {
                document.documentElement.classList.toggle('dark', theme === 'dark');
                set({ theme });
            },
        }),
        {
            name: 'jarvis-ui',
        }
    )
);
