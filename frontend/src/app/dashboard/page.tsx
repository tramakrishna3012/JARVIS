'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Briefcase, FileText, Send, Users, Mail, TrendingUp, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { applicationsApi, jobsApi, resumesApi, emailsApi } from '../../lib/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
    const { data: stats } = useQuery({
        queryKey: ['application-stats'],
        queryFn: () => applicationsApi.stats().then(r => r.data),
    });

    const { data: jobs } = useQuery({
        queryKey: ['recent-jobs'],
        queryFn: () => jobsApi.list({ limit: 5 }).then(r => r.data),
    });

    const { data: emailStats } = useQuery({
        queryKey: ['email-stats'],
        queryFn: () => emailsApi.stats().then(r => r.data),
    });

    const statCards = [
        { label: 'Jobs Discovered', value: jobs?.length || 0, icon: Briefcase, color: 'bg-blue-500' },
        { label: 'Applications', value: stats?.total || 0, icon: Send, color: 'bg-green-500' },
        { label: 'Interviews', value: stats?.interviewing || 0, icon: CheckCircle2, color: 'bg-purple-500' },
        { label: 'Pending Emails', value: emailStats?.pending_replies || 0, icon: Mail, color: 'bg-orange-500' },
    ];

    // Mock chart data
    const chartData = [
        { name: 'Mon', applications: 4, interviews: 1 },
        { name: 'Tue', applications: 3, interviews: 0 },
        { name: 'Wed', applications: 5, interviews: 2 },
        { name: 'Thu', applications: 2, interviews: 1 },
        { name: 'Fri', applications: 6, interviews: 1 },
        { name: 'Sat', applications: 1, interviews: 0 },
        { name: 'Sun', applications: 2, interviews: 0 },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Dashboard</h1>
                <p className="text-dark-500 dark:text-dark-400 mt-1">
                    Welcome back! Here's your job search overview.
                </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="card"
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-dark-500 dark:text-dark-400 text-sm">{stat.label}</p>
                                <p className="text-3xl font-bold text-dark-900 dark:text-white mt-1">
                                    {stat.value}
                                </p>
                            </div>
                            <div className={`w-12 h-12 rounded-lg ${stat.color} flex items-center justify-center`}>
                                <stat.icon className="w-6 h-6 text-white" />
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Activity Chart */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">
                        Weekly Activity
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorApps" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="name" stroke="#64748b" />
                                <YAxis stroke="#64748b" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1e293b',
                                        border: 'none',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="applications"
                                    stroke="#3b82f6"
                                    fillOpacity={1}
                                    fill="url(#colorApps)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Application Status */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">
                        Application Status
                    </h3>
                    <div className="space-y-4">
                        {[
                            { label: 'Submitted', value: stats?.submitted || 0, color: 'bg-blue-500', pct: 40 },
                            { label: 'Interviewing', value: stats?.interviewing || 0, color: 'bg-purple-500', pct: 25 },
                            { label: 'Offered', value: stats?.offered || 0, color: 'bg-green-500', pct: 15 },
                            { label: 'Rejected', value: stats?.rejected || 0, color: 'bg-red-500', pct: 20 },
                        ].map((item) => (
                            <div key={item.label}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-dark-600 dark:text-dark-400">{item.label}</span>
                                    <span className="font-medium text-dark-900 dark:text-white">{item.value}</span>
                                </div>
                                <div className="w-full bg-dark-200 dark:bg-dark-700 rounded-full h-2">
                                    <div
                                        className={`${item.color} h-2 rounded-full transition-all`}
                                        style={{ width: `${item.pct}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Jobs */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-dark-900 dark:text-white">
                        Recent Job Discoveries
                    </h3>
                    <a href="/dashboard/jobs" className="text-primary-500 hover:text-primary-600 text-sm">
                        View all →
                    </a>
                </div>
                <div className="space-y-3">
                    {jobs?.slice(0, 5).map((job: any) => (
                        <div
                            key={job.id}
                            className="flex items-center justify-between p-4 rounded-lg bg-dark-50 dark:bg-dark-800"
                        >
                            <div>
                                <h4 className="font-medium text-dark-900 dark:text-white">{job.title}</h4>
                                <p className="text-sm text-dark-500 dark:text-dark-400">
                                    {job.company} • {job.location || 'Remote'}
                                </p>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`badge ${job.relevance_score >= 0.7 ? 'badge-success' : 'badge-info'}`}>
                                    {Math.round(job.relevance_score * 100)}% match
                                </span>
                                <button className="btn-primary text-sm py-1.5">Apply</button>
                            </div>
                        </div>
                    ))}
                    {(!jobs || jobs.length === 0) && (
                        <p className="text-center text-dark-500 py-8">
                            No jobs discovered yet. Start by triggering a job discovery.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
