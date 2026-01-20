'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Rocket, Mail, Lock, ArrowRight, Check } from 'lucide-react';
import { authApi } from '../../lib/api';
import { useAuthStore } from '../../lib/store';

interface RegisterForm {
    email: string;
    password: string;
    confirmPassword: string;
}

export default function RegisterPage() {
    const router = useRouter();
    const { login } = useAuthStore();
    const [error, setError] = useState('');

    const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterForm>();
    const password = watch('password');

    const mutation = useMutation({
        mutationFn: (data: RegisterForm) => authApi.register(data.email, data.password),
        onSuccess: (response) => {
            const { user, tokens } = response.data;
            login(user, tokens.access_token, tokens.refresh_token);
            router.push('/dashboard/settings'); // Go to settings to complete profile
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        },
    });

    const onSubmit = (data: RegisterForm) => {
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
                    <h1 className="text-2xl font-bold text-white text-center mb-2">
                        Create Your Account
                    </h1>
                    <p className="text-dark-400 text-center mb-6">
                        Start automating your job search today
                    </p>

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
                                    {...register('email', {
                                        required: 'Email is required',
                                        pattern: {
                                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                            message: 'Invalid email address'
                                        }
                                    })}
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
                                    {...register('password', {
                                        required: 'Password is required',
                                        minLength: {
                                            value: 8,
                                            message: 'Password must be at least 8 characters'
                                        }
                                    })}
                                    className="input pl-10 bg-dark-700 border-dark-600"
                                    placeholder="••••••••"
                                />
                            </div>
                            {errors.password && (
                                <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
                            )}
                        </div>

                        <div>
                            <label className="label text-dark-300">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                                <input
                                    type="password"
                                    {...register('confirmPassword', {
                                        required: 'Please confirm your password',
                                        validate: value => value === password || 'Passwords do not match'
                                    })}
                                    className="input pl-10 bg-dark-700 border-dark-600"
                                    placeholder="••••••••"
                                />
                            </div>
                            {errors.confirmPassword && (
                                <p className="text-red-400 text-sm mt-1">{errors.confirmPassword.message}</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={mutation.isPending}
                            className="btn-primary w-full py-3"
                        >
                            {mutation.isPending ? 'Creating account...' : 'Create Account'}
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </button>
                    </form>

                    {/* Features */}
                    <div className="mt-6 pt-6 border-t border-dark-700">
                        <p className="text-dark-400 text-sm mb-3">What you'll get:</p>
                        <ul className="space-y-2">
                            {['AI-powered job matching', 'Automated resume generation', 'Smart referral management'].map((feature) => (
                                <li key={feature} className="flex items-center gap-2 text-dark-300 text-sm">
                                    <Check className="w-4 h-4 text-green-500" />
                                    {feature}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="mt-6 text-center text-dark-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-primary-400 hover:text-primary-300">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
