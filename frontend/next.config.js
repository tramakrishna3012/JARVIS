/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,

    // Compiler optimizations
    compiler: {
        // Remove console.logs in production
        removeConsole: process.env.NODE_ENV === 'production',
    },

    // Experimental performance features
    experimental: {
        // Optimize package imports for smaller bundles
        optimizePackageImports: ['lucide-react', 'framer-motion', 'recharts', '@tanstack/react-query'],
    },

    // API rewrites to backend
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.NEXT_PUBLIC_API_URL
                    ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
                    : 'http://localhost:8000/api/:path*',
            },
        ];
    },

    // Compression headers for better caching
    async headers() {
        return [
            {
                source: '/:all*(svg|jpg|png|webp|avif)',
                headers: [
                    {
                        key: 'Cache-Control',
                        value: 'public, max-age=31536000, immutable',
                    },
                ],
            },
            {
                source: '/_next/static/:path*',
                headers: [
                    {
                        key: 'Cache-Control',
                        value: 'public, max-age=31536000, immutable',
                    },
                ],
            },
        ];
    },

    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },

    // Image optimization
    images: {
        domains: ['avatars.githubusercontent.com', 'lh3.googleusercontent.com'],
        formats: ['image/avif', 'image/webp'],
        minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
    },

    // Reduce bundle size by excluding source maps in production
    productionBrowserSourceMaps: false,

    // Power pack
    poweredByHeader: false,
};

module.exports = nextConfig;
