import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
    title: 'JARVIS - AI Job Application Platform',
    description: 'AI-powered automated job application and referral platform',
    keywords: ['job search', 'resume builder', 'job application', 'AI', 'automation'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className="min-h-screen bg-dark-50 dark:bg-dark-950 antialiased">
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
