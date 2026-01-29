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
    login: (user: User, accessToken: string, refreshToken: string, remember?: boolean) => void;
    logout: () => void;
    checkAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            profile: null,
            isAuthenticated: false,

            setUser: (user) => set({ user, isAuthenticated: !!user }),

            setProfile: (profile) => set({ profile }),

            login: (user, accessToken, refreshToken, remember = true) => {
                if (remember) {
                    localStorage.setItem('access_token', accessToken);
                    localStorage.setItem('refresh_token', refreshToken);
                } else {
                    sessionStorage.setItem('access_token', accessToken);
                    sessionStorage.setItem('refresh_token', refreshToken);
                }
                set({ user, isAuthenticated: true });
            },

            logout: () => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('refresh_token');
                set({ user: null, profile: null, isAuthenticated: false });
            },

            checkAuth: () => {
                const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
                if (token) {
                    // Token exists, mark as authenticated
                    set((state) => ({ isAuthenticated: !!state.user || !!token }));
                } else {
                    set({ isAuthenticated: false, user: null });
                }
            },
        }),
        {
            name: 'jarvis-auth',
            partialize: (state) => ({
                user: state.user,
                profile: state.profile,
                isAuthenticated: state.isAuthenticated
            }),
            onRehydrateStorage: () => (state) => {
                // Verify token exists when rehydrating
                if (typeof window !== 'undefined') {
                    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
                    if (state && token) {
                        state.isAuthenticated = true;
                    } else if (state && !token) {
                        state.isAuthenticated = false;
                        state.user = null;
                    }
                }
            },
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
