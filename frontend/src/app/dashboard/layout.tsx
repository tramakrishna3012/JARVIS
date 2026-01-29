'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, Briefcase, FileText, Send, Users, Mail,
    Settings, LogOut, Menu, X, Moon, Sun, ChevronLeft
} from 'lucide-react';
import { useUIStore, useAuthStore } from '../../lib/store';
import { motion, AnimatePresence } from 'framer-motion';

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    const pathname = usePathname();
    const { sidebarOpen, toggleSidebar, theme, setTheme } = useUIStore();
    const { user, logout } = useAuthStore();

    const navItems = [
        { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { href: '/dashboard/jobs', icon: Briefcase, label: 'Jobs' },
        { href: '/dashboard/resumes', icon: FileText, label: 'Resumes' },
        { href: '/dashboard/applications', icon: Send, label: 'Applications' },
        { href: '/dashboard/referrals', icon: Users, label: 'Referrals' },
        { href: '/dashboard/emails', icon: Mail, label: 'Emails' },
        { href: '/dashboard/settings', icon: Settings, label: 'Settings' },
    ];

    return (
        <div className="min-h-screen bg-dark-50 dark:bg-dark-950 flex">
            {/* Sidebar */}
            <AnimatePresence mode="wait">
                {sidebarOpen && (
                    <motion.aside
                        initial={{ x: -256 }}
                        animate={{ x: 0 }}
                        exit={{ x: -256 }}
                        transition={{ duration: 0.2 }}
                        className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-dark-900 border-r border-dark-200 dark:border-dark-800 lg:relative"
                    >
                        <div className="flex flex-col h-full">
                            {/* Logo */}
                            <Link href="/" className="flex items-center gap-3 px-6 py-4 border-b border-dark-200 dark:border-dark-800 hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors">
                                <Image src="/jarvis.svg" alt="JARVIS" width={56} height={56} className="object-contain" />
                                <span className="text-lg font-bold text-dark-900 dark:text-white">JARVIS</span>
                            </Link>

                            {/* Navigation */}
                            <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                                {navItems.map((item) => {
                                    const isActive = pathname === item.href;
                                    return (
                                        <Link
                                            key={item.href}
                                            href={item.href}
                                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                                                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                                                : 'text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800'
                                                }`}
                                        >
                                            <item.icon className="w-5 h-5" />
                                            <span className="font-medium">{item.label}</span>
                                        </Link>
                                    );
                                })}
                            </nav>

                            {/* Footer */}
                            <div className="p-4 border-t border-dark-200 dark:border-dark-800">
                                <div className="flex items-center gap-3 px-4 py-2 text-dark-600 dark:text-dark-400">
                                    <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                                        <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                                            {user?.email?.charAt(0).toUpperCase() || 'U'}
                                        </span>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium truncate">{user?.email}</p>
                                    </div>
                                </div>

                                <Link
                                    href="/"
                                    className="w-full flex items-center gap-3 px-4 py-3 mt-2 text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 rounded-lg transition-colors"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                    <span>Back to Home</span>
                                </Link>

                                <button
                                    onClick={logout}
                                    className="w-full flex items-center gap-3 px-4 py-3 mt-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                >
                                    <LogOut className="w-5 h-5" />
                                    <span>Logout</span>
                                </button>
                            </div>
                        </div>
                    </motion.aside>
                )}
            </AnimatePresence>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-h-screen">
                {/* Top Bar */}
                <header className="sticky top-0 z-40 bg-white dark:bg-dark-900 border-b border-dark-200 dark:border-dark-800">
                    <div className="flex items-center justify-between px-6 py-4">
                        <button
                            onClick={toggleSidebar}
                            className="p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
                        >
                            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                        </button>

                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                                className="p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
                            >
                                {theme === 'dark' ? (
                                    <Sun className="w-5 h-5 text-yellow-500" />
                                ) : (
                                    <Moon className="w-5 h-5 text-dark-600" />
                                )}
                            </button>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 p-6 overflow-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}
