/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,

    // API rewrites to backend
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.BACKEND_URL
                    ? `${process.env.BACKEND_URL}/api/:path*`
                    : 'http://localhost:8000/api/:path*',
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
    },
};

module.exports = nextConfig;
