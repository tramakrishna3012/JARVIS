'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Rocket, Mail, Lock, ArrowRight } from 'lucide-react';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

interface LoginForm {
    email: string;
    password: string;
}

export default function LoginPage() {
    const router = useRouter();
    const { login } = useAuthStore();
    const [error, setError] = useState('');

    const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

    const mutation = useMutation({
        mutationFn: (data: LoginForm) => authApi.login(data.email, data.password),
        onSuccess: (response) => {
            const { user, tokens } = response.data;
            login(user, tokens.access_token, tokens.refresh_token);
            router.push('/dashboard');
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        },
    });

    const onSubmit = (data: LoginForm) => {
        setError('');
        mutation.mutate(data);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-950 to-primary-950 flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="flex items-center justify-center gap-3 mb-8">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                        <Rocket className="w-7 h-7 text-white" />
                    </div>
                    <span className="text-3xl font-bold text-white">JARVIS</span>
                </div>

                {/* Card */}
                <div className="card bg-dark-800/50 backdrop-blur border-dark-700">
                    <h1 className="text-2xl font-bold text-white text-center mb-6">
                        Welcome Back
                    </h1>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div>
                            <label className="label text-dark-300">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                <input
                                    type="email"
                                    {...register('email', { required: 'Email is required' })}
                                    className="input pl-10 bg-dark-700 border-dark-600"
                                    placeholder="you@example.com"
                                />
                            </div>
                            {errors.email && (
                                <p className="text-red-400 text-sm mt-1">{errors.email.message}</p>
                            )}
                        </div>

                        <div>
                            <label className="label text-dark-300">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                <input
                                    type="password"
                                    {...register('password', { required: 'Password is required' })}
                                    className="input pl-10 bg-dark-700 border-dark-600"
                                    placeholder="••••••••"
                                />
                            </div>
                            {errors.password && (
                                <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={mutation.isPending}
                            className="btn-primary w-full py-3"
                        >
                            {mutation.isPending ? 'Signing in...' : 'Sign In'}
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </button>
                    </form>

                    <div className="mt-6 text-center text-dark-400">
                        Don't have an account?{' '}
                        <Link href="/register" className="text-primary-400 hover:text-primary-300">
                            Sign up
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
