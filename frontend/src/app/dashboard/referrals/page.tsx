'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Users, UserPlus, MessageSquare, CheckCircle, Clock, XCircle, Search, Filter } from 'lucide-react';
import { referralsApi } from '@/lib/api';

export default function ReferralsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const queryClient = useQueryClient();

    const { data: referrals, isLoading } = useQuery({
        queryKey: ['referrals', statusFilter],
        queryFn: () => referralsApi.list({ status: statusFilter !== 'all' ? statusFilter : undefined }),
    });

    const statusBadges: Record<string, { color: string; icon: typeof CheckCircle }> = {
        pending: { color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400', icon: Clock },
        accepted: { color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', icon: CheckCircle },
        declined: { color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: XCircle },
        contacted: { color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', icon: MessageSquare },
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-dark-900 dark:text-white">Referrals</h1>
                    <p className="text-dark-500 dark:text-dark-400">Manage your referral requests and connections</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <UserPlus className="w-4 h-4" />
                    Request Referral
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Referrals', value: referrals?.data?.length || 0, color: 'bg-primary-500' },
                    { label: 'Pending', value: referrals?.data?.filter((r: any) => r.status === 'pending').length || 0, color: 'bg-yellow-500' },
                    { label: 'Accepted', value: referrals?.data?.filter((r: any) => r.status === 'accepted').length || 0, color: 'bg-green-500' },
                    { label: 'Contacted', value: referrals?.data?.filter((r: any) => r.status === 'contacted').length || 0, color: 'bg-blue-500' },
                ].map((stat) => (
                    <div key={stat.label} className="card p-4">
                        <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg ${stat.color} flex items-center justify-center`}>
                                <Users className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-dark-900 dark:text-white">{stat.value}</p>
                                <p className="text-sm text-dark-500">{stat.label}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                    <input
                        type="text"
                        placeholder="Search referrals..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input pl-10 w-full"
                    />
                </div>
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="input"
                >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="contacted">Contacted</option>
                    <option value="accepted">Accepted</option>
                    <option value="declined">Declined</option>
                </select>
            </div>

            {/* Referrals List */}
            <div className="card overflow-hidden">
                {isLoading ? (
                    <div className="p-8 text-center text-dark-500">Loading referrals...</div>
                ) : referrals?.data?.length === 0 ? (
                    <div className="p-12 text-center">
                        <Users className="w-12 h-12 mx-auto text-dark-300 dark:text-dark-600 mb-4" />
                        <h3 className="text-lg font-medium text-dark-900 dark:text-white mb-2">No referrals yet</h3>
                        <p className="text-dark-500 dark:text-dark-400 mb-4">
                            Start building your network by requesting referrals.
                        </p>
                        <button className="btn-primary">
                            <UserPlus className="w-4 h-4 mr-2" />
                            Request Your First Referral
                        </button>
                    </div>
                ) : (
                    <table className="w-full">
                        <thead className="bg-dark-50 dark:bg-dark-800">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase">Contact</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase">Company</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase">Position</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-dark-200 dark:divide-dark-700">
                            {referrals?.data?.map((referral: any) => {
                                const badge = statusBadges[referral.status] || statusBadges.pending;
                                const StatusIcon = badge.icon;
                                return (
                                    <tr key={referral.id} className="hover:bg-dark-50 dark:hover:bg-dark-800">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                                                    <span className="text-sm font-medium text-primary-600">
                                                        {referral.contact_name?.charAt(0) || 'R'}
                                                    </span>
                                                </div>
                                                <span className="font-medium text-dark-900 dark:text-white">
                                                    {referral.contact_name || 'Unknown'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-dark-600 dark:text-dark-400">{referral.company}</td>
                                        <td className="px-6 py-4 text-dark-600 dark:text-dark-400">{referral.position}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
                                                <StatusIcon className="w-3 h-3" />
                                                {referral.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-dark-500 text-sm">{referral.created_at}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </motion.div>
    );
}
