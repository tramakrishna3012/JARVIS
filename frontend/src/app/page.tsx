'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Rocket, Briefcase, FileText, Mail, Users, Zap, ChevronRight } from 'lucide-react';

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-950 to-primary-950">
            {/* Hero Section */}
            <header className="container mx-auto px-6 py-8">
                <nav className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                            <Rocket className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-2xl font-bold text-white">JARVIS</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-dark-300 hover:text-white transition-colors">
                            Login
                        </Link>
                        <Link href="/register" className="btn-primary">
                            Get Started
                        </Link>
                    </div>
                </nav>
            </header>

            <main>
                {/* Hero */}
                <section className="container mx-auto px-6 py-20 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <span className="badge-info mb-4">AI-Powered Job Automation</span>
                        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                            Your AI Career
                            <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                                {' '}Assistant
                            </span>
                        </h1>
                        <p className="text-xl text-dark-300 max-w-2xl mx-auto mb-8">
                            Automate your job search with AI. Discover opportunities, generate tailored resumes,
                            apply automatically, and manage referrals - all in one platform.
                        </p>
                        <div className="flex gap-4 justify-center">
                            <Link href="/register" className="btn-primary text-lg px-8 py-3">
                                Start Free Trial
                                <ChevronRight className="w-5 h-5 ml-2" />
                            </Link>
                            <Link href="#features" className="btn-secondary text-lg px-8 py-3">
                                Learn More
                            </Link>
                        </div>
                    </motion.div>
                </section>

                {/* Features */}
                <section id="features" className="container mx-auto px-6 py-20">
                    <h2 className="text-3xl font-bold text-white text-center mb-12">
                        Everything You Need to Land Your Dream Job
                    </h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <motion.div
                                key={feature.title}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: index * 0.1 }}
                                className="card bg-dark-800/50 backdrop-blur border-dark-700"
                            >
                                <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-4`}>
                                    <feature.icon className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                                <p className="text-dark-400">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* Stats */}
                <section className="container mx-auto px-6 py-20">
                    <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-12">
                        <div className="grid md:grid-cols-4 gap-8 text-center">
                            {stats.map((stat) => (
                                <div key={stat.label}>
                                    <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                                    <div className="text-primary-200">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="container mx-auto px-6 py-8 border-t border-dark-800">
                <div className="flex items-center justify-between">
                    <div className="text-dark-500">© 2024 JARVIS. All rights reserved.</div>
                    <div className="flex gap-6 text-dark-400">
                        <Link href="/privacy" className="hover:text-white">Privacy</Link>
                        <Link href="/terms" className="hover:text-white">Terms</Link>
                        <Link href="/contact" className="hover:text-white">Contact</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}

const features = [
    {
        icon: Briefcase,
        title: 'Smart Job Discovery',
        description: 'AI scans LinkedIn, Naukri, and company pages to find jobs matching your skills and preferences.',
        color: 'bg-blue-500',
    },
    {
        icon: FileText,
        title: 'AI Resume Builder',
        description: 'Generate ATS-optimized, tailored resumes for each application using your real experience.',
        color: 'bg-green-500',
    },
    {
        icon: Zap,
        title: 'Auto-Apply Bot',
        description: 'Automatically fill forms, answer screening questions, and submit applications for you.',
        color: 'bg-yellow-500',
    },
    {
        icon: Users,
        title: 'Referral Management',
        description: 'Find connections at target companies and send personalized referral requests.',
        color: 'bg-purple-500',
    },
    {
        icon: Mail,
        title: 'Email Intelligence',
        description: 'Track all job-related emails, get AI summaries, and never miss a follow-up.',
        color: 'bg-pink-500',
    },
    {
        icon: Rocket,
        title: 'AI Decision Engine',
        description: 'Smart scoring and matching to focus on the best opportunities for you.',
        color: 'bg-orange-500',
    },
];

const stats = [
    { value: '10K+', label: 'Jobs Discovered' },
    { value: '5K+', label: 'Resumes Generated' },
    { value: '85%', label: 'Interview Rate' },
    { value: '2.5x', label: 'Faster Job Search' },
];
