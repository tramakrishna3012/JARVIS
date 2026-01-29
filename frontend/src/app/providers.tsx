'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';

export function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        // Cache data for 5 minutes
                        staleTime: 5 * 60 * 1000,
                        // Keep unused data in cache for 30 minutes
                        gcTime: 30 * 60 * 1000,
                        // Only retry once on failure
                        retry: 1,
                        // Don't refetch on window focus (reduces API calls)
                        refetchOnWindowFocus: false,
                        // Don't refetch on reconnect immediately
                        refetchOnReconnect: 'always',
                        // Enable structural sharing for better performance
                        structuralSharing: true,
                    },
                    mutations: {
                        retry: 1,
                    },
                },
            })
    );

    // Hydrate auth state from localStorage on mount
    const { checkAuth } = useAuthStore();
    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    return (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
}
