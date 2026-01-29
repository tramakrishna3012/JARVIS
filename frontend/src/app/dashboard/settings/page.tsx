'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Lock, Bell, Save, Shield } from 'lucide-react';
import { useAuthStore } from '../../../lib/store';

export default function SettingsPage() {
    const { user } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsLoading(false);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Settings</h1>
                <p className="text-dark-500 dark:text-dark-400 mt-1">
                    Manage your account settings and preferences.
                </p>
            </div>

            <div className="grid gap-8">
                {/* Profile Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card"
                >
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <User className="w-5 h-5 text-blue-500" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-dark-900 dark:text-white">Profile Information</h2>
                            <p className="text-sm text-dark-500 dark:text-dark-400">Update your personal details</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="label">Full Name</label>
                                <input
                                    type="text"
                                    className="input"
                                    defaultValue={user?.full_name || ''}
                                    placeholder="John Doe"
                                />
                            </div>
                            <div>
                                <label className="label">Email Address</label>
                                <input
                                    type="email"
                                    className="input bg-dark-50 dark:bg-dark-900/50"
                                    defaultValue={user?.email || ''}
                                    disabled
                                />
                                <p className="text-xs text-dark-500 mt-1">Email cannot be changed</p>
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <button type="submit" className="btn-primary" disabled={isLoading}>
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Saving...
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-2">
                                        <Save className="w-4 h-4" />
                                        Save Changes
                                    </span>
                                )}
                            </button>
                        </div>
                    </form>
                </motion.div>

                {/* Password Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card"
                >
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                            <Lock className="w-5 h-5 text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-dark-900 dark:text-white">Security</h2>
                            <p className="text-sm text-dark-500 dark:text-dark-400">Manage your password and security</p>
                        </div>
                    </div>

                    <form className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="label">Current Password</label>
                                <input type="password" className="input" placeholder="••••••••" />
                            </div>
                            <div className="md:col-span-2 grid md:grid-cols-2 gap-4">
                                <div>
                                    <label className="label">New Password</label>
                                    <input type="password" className="input" placeholder="••••••••" />
                                </div>
                                <div>
                                    <label className="label">Confirm New Password</label>
                                    <input type="password" className="input" placeholder="••••••••" />
                                </div>
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <button type="button" className="btn-secondary">
                                Update Password
                            </button>
                        </div>
                    </form>
                </motion.div>

                {/* API Keys Section (Placeholder for future) */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="card"
                >
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                            <Shield className="w-5 h-5 text-green-500" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-dark-900 dark:text-white">API Configuration</h2>
                            <p className="text-sm text-dark-500 dark:text-dark-400">Manage your external service keys</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="label">OpenAI API Key</label>
                            <div className="flex gap-2">
                                <input
                                    type="password"
                                    className="input flex-1"
                                    placeholder="sk-..."
                                    defaultValue=""
                                />
                                <button className="btn-secondary whitespace-nowrap">Update Key</button>
                            </div>
                            <p className="text-xs text-dark-500 mt-1">Used for AI resume generation</p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
