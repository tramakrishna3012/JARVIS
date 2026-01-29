'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Mail, Send, Inbox, Trash2, Star, Plus, Search } from 'lucide-react';
import { emailsApi } from '@/lib/api';

export default function EmailsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [activeTab, setActiveTab] = useState<'inbox' | 'sent' | 'drafts'>('inbox');
    const queryClient = useQueryClient();

    const { data: emails, isLoading } = useQuery({
        queryKey: ['emails', activeTab],
        queryFn: () => emailsApi.list({ folder: activeTab }),
    });

    const tabs = [
        { id: 'inbox', label: 'Inbox', icon: Inbox },
        { id: 'sent', label: 'Sent', icon: Send },
        { id: 'drafts', label: 'Drafts', icon: Mail },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-dark-900 dark:text-white">Emails</h1>
                    <p className="text-dark-500 dark:text-dark-400">Manage your email communications</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Compose Email
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-dark-200 dark:border-dark-700">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as typeof activeTab)}
                        className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${activeTab === tab.id
                                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                                : 'border-transparent text-dark-500 hover:text-dark-700 dark:hover:text-dark-300'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                    type="text"
                    placeholder="Search emails..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input pl-10 w-full"
                />
            </div>

            {/* Email List */}
            <div className="card divide-y divide-dark-200 dark:divide-dark-700">
                {isLoading ? (
                    <div className="p-8 text-center text-dark-500">Loading emails...</div>
                ) : emails?.data?.length === 0 ? (
                    <div className="p-12 text-center">
                        <Mail className="w-12 h-12 mx-auto text-dark-300 dark:text-dark-600 mb-4" />
                        <h3 className="text-lg font-medium text-dark-900 dark:text-white mb-2">No emails yet</h3>
                        <p className="text-dark-500 dark:text-dark-400">
                            Your {activeTab} is empty. Start by composing an email.
                        </p>
                    </div>
                ) : (
                    emails?.data?.map((email: any) => (
                        <div
                            key={email.id}
                            className="flex items-center gap-4 p-4 hover:bg-dark-50 dark:hover:bg-dark-800 cursor-pointer transition-colors"
                        >
                            <button className="text-dark-400 hover:text-yellow-500">
                                <Star className={`w-5 h-5 ${email.starred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                            </button>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className={`font-medium ${email.read ? 'text-dark-600' : 'text-dark-900 dark:text-white'}`}>
                                        {email.from || email.to}
                                    </span>
                                    <span className="text-xs text-dark-400">{email.date}</span>
                                </div>
                                <p className="text-sm text-dark-900 dark:text-white truncate">{email.subject}</p>
                                <p className="text-sm text-dark-500 truncate">{email.preview}</p>
                            </div>
                            <button className="text-dark-400 hover:text-red-500">
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    ))
                )}
            </div>
        </motion.div>
    );
}
