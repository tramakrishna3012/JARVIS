'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Search, Filter, Plus, MapPin, Building2, Clock, ExternalLink, Star, Trash2 } from 'lucide-react';
import { jobsApi } from '@/lib/api';
import type { Job, JobStatus } from '@/types';

const statusColors: Record<JobStatus, string> = {
    discovered: 'badge-info',
    interested: 'badge-warning',
    applied: 'badge-success',
    interviewing: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    offered: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    rejected: 'badge-error',
    withdrawn: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
    expired: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
};

export default function JobsPage() {
    const queryClient = useQueryClient();
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('');
    const [countryFilter, setCountryFilter] = useState<string>('');

    const { data: jobs, isLoading } = useQuery({
        queryKey: ['jobs', search, statusFilter, countryFilter],
        queryFn: () => jobsApi.list({
            search,
            status: statusFilter || undefined,
            country: countryFilter || undefined,
        }).then(r => r.data),
    });

    const updateJobMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: any }) => jobsApi.update(id, data),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
    });

    const discoverMutation = useMutation({
        mutationFn: () => jobsApi.discover({
            sources: ['linkedin', 'naukri'],
            keywords: ['software engineer', 'developer'],
        }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Jobs</h1>
                    <p className="text-dark-500 dark:text-dark-400 mt-1">
                        Discover and track job opportunities
                    </p>
                </div>
                <button
                    onClick={() => discoverMutation.mutate()}
                    disabled={discoverMutation.isPending}
                    className="btn-primary"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    {discoverMutation.isPending ? 'Discovering...' : 'Discover Jobs'}
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4">
                <div className="relative flex-1 min-w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                    <input
                        type="text"
                        placeholder="Search jobs..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="input pl-10"
                    />
                </div>
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="input w-auto"
                >
                    <option value="">All Status</option>
                    <option value="discovered">Discovered</option>
                    <option value="interested">Interested</option>
                    <option value="applied">Applied</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="offered">Offered</option>
                </select>
                <select
                    value={countryFilter}
                    onChange={(e) => setCountryFilter(e.target.value)}
                    className="input w-auto"
                >
                    <option value="">All Countries</option>
                    <option value="India">India</option>
                    <option value="USA">USA</option>
                    <option value="UK">UK</option>
                    <option value="Remote">Remote</option>
                </select>
            </div>

            {/* Job Cards */}
            {isLoading ? (
                <div className="flex justify-center py-12">
                    <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : (
                <div className="grid gap-4">
                    {jobs?.map((job: Job, index: number) => (
                        <motion.div
                            key={job.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="card hover:border-primary-500/50"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="text-lg font-semibold text-dark-900 dark:text-white">
                                            {job.title}
                                        </h3>
                                        <span className={`badge ${statusColors[job.status]}`}>
                                            {job.status}
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-4 text-sm text-dark-500 dark:text-dark-400">
                                        <span className="flex items-center gap-1">
                                            <Building2 className="w-4 h-4" />
                                            {job.company}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <MapPin className="w-4 h-4" />
                                            {job.location || job.country || 'Remote'}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-4 h-4" />
                                            {new Date(job.discovered_at).toLocaleDateString()}
                                        </span>
                                    </div>

                                    {/* Skills */}
                                    {job.required_skills?.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {job.required_skills.slice(0, 5).map((skill) => (
                                                <span
                                                    key={skill}
                                                    className="px-2 py-1 text-xs rounded bg-dark-100 dark:bg-dark-700 text-dark-600 dark:text-dark-300"
                                                >
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Score & Actions */}
                                <div className="flex flex-col items-end gap-3">
                                    <div className="flex items-center gap-2">
                                        <Star className={`w-5 h-5 ${job.relevance_score >= 0.7 ? 'text-yellow-500' : 'text-dark-400'}`} />
                                        <span className="text-lg font-bold text-dark-900 dark:text-white">
                                            {Math.round(job.relevance_score * 100)}%
                                        </span>
                                    </div>

                                    <div className="flex gap-2">
                                        {job.apply_url && (
                                            <a
                                                href={job.apply_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn-ghost p-2"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </a>
                                        )}
                                        <button
                                            onClick={() => updateJobMutation.mutate({
                                                id: job.id,
                                                data: { status: 'interested' }
                                            })}
                                            className="btn-secondary text-sm py-1.5"
                                        >
                                            Mark Interested
                                        </button>
                                        <button className="btn-primary text-sm py-1.5">
                                            Apply
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}

                    {(!jobs || jobs.length === 0) && (
                        <div className="card text-center py-12">
                            <p className="text-dark-500 dark:text-dark-400">
                                No jobs found. Try adjusting your filters or discovering new jobs.
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
