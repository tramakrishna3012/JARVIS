'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Mail, Lock, ArrowRight, ChevronLeft } from 'lucide-react';
import { authApi } from '../../lib/api';
import { useAuthStore } from '../../lib/store';

interface LoginForm {
    email: string;
    password: string;
    rememberMe?: boolean;
}

export default function LoginPage() {
    const router = useRouter();
    const { login } = useAuthStore();
    const [error, setError] = useState('');

    const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

    const mutation = useMutation({
        mutationFn: (data: LoginForm) => authApi.login(data.email, data.password),
        onSuccess: (response, variables) => {
            const { user, tokens } = response.data;
            login(user, tokens.access_token, tokens.refresh_token, variables.rememberMe);
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
        <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-950 to-primary-950 flex items-center justify-center px-4 relative">
            {/* Back to Home */}
            <Link href="/" className="absolute top-8 left-8 flex items-center gap-2 text-dark-300 hover:text-white transition-colors">
                <ChevronLeft className="w-5 h-5" />
                <span>Back to Home</span>
            </Link>

            <div className="w-full max-w-md">
                {/* Logo */}
                <Link href="/" className="flex items-center justify-center gap-3 mb-8 hover:opacity-80 transition-opacity">
                    <Image src="/jarvis.svg" alt="JARVIS" width={72} height={72} className="object-contain" />
                    <span className="text-xl font-bold text-white">JARVIS</span>
                </Link>

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

                        {/* Remember Me */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    {...register('rememberMe')}
                                    className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-500 focus:ring-primary-500 focus:ring-offset-dark-800"
                                />
                                <span className="text-sm text-dark-400">Remember me</span>
                            </label>
                            <Link href="/forgot-password" className="text-sm text-primary-400 hover:text-primary-300">
                                Forgot password?
                            </Link>
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
