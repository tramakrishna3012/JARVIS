'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Send, Clock, CheckCircle2, XCircle, MoreVertical, ExternalLink } from 'lucide-react';
import { applicationsApi } from '../../../lib/api';

const statusConfig = {
    applied: { icon: Send, color: 'text-blue-500', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    interviewing: { icon: Clock, color: 'text-purple-500', bg: 'bg-purple-100 dark:bg-purple-900/30' },
    offered: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-100 dark:bg-green-900/30' },
    rejected: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100 dark:bg-red-900/30' },
};

export default function ApplicationsPage() {
    const { data: applications, isLoading } = useQuery({
        queryKey: ['applications'],
        queryFn: () => applicationsApi.list().then(r => r.data),
    });

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Applications</h1>
                    <p className="text-dark-500 dark:text-dark-400 mt-1">
                        Track and manage your job applications
                    </p>
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-12">
                    <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : (
                <div className="card overflow-hidden p-0">
                    <table className="w-full text-left">
                        <thead className="bg-dark-50 dark:bg-dark-800/50 text-dark-500 dark:text-dark-400 text-sm font-medium">
                            <tr>
                                <th className="px-6 py-4">Company & Role</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Applied Date</th>
                                <th className="px-6 py-4">Job Board</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-dark-100 dark:divide-dark-800">
                            {applications?.map((app: any, index: number) => {
                                const StatusIcon = statusConfig[app.status as keyof typeof statusConfig]?.icon || Send;
                                const statusStyle = statusConfig[app.status as keyof typeof statusConfig] || statusConfig.applied;

                                return (
                                    <motion.tr
                                        key={app.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        className="hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors"
                                    >
                                        <td className="px-6 py-4">
                                            <div>
                                                <div className="font-medium text-dark-900 dark:text-white">
                                                    {app.job_title}
                                                </div>
                                                <div className="text-sm text-dark-500 dark:text-dark-400">
                                                    {app.company_name}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusStyle.bg} ${statusStyle.color}`}>
                                                <StatusIcon className="w-3.5 h-3.5" />
                                                <span className="capitalize">{app.status}</span>
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-dark-600 dark:text-dark-300">
                                            {new Date(app.applied_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-dark-600 dark:text-dark-300">
                                            {app.job_board || 'Direct'}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                {app.job_url && (
                                                    <a
                                                        href={app.job_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="btn-ghost p-2 text-dark-400 hover:text-primary-500"
                                                    >
                                                        <ExternalLink className="w-4 h-4" />
                                                    </a>
                                                )}
                                                <button className="btn-ghost p-2 text-dark-400 hover:text-dark-900 dark:hover:text-white">
                                                    <MoreVertical className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                );
                            })}
                        </tbody>
                    </table>

                    {(!applications || applications.length === 0) && (
                        <div className="text-center py-12">
                            <Send className="w-12 h-12 text-dark-300 mx-auto mb-3" />
                            <p className="text-dark-500 dark:text-dark-400">
                                No applications yet. Start applying to jobs!
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
