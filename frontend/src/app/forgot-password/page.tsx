'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

interface ForgotPasswordForm {
    email: string;
}

export default function ForgotPasswordPage() {
    const [isSubmitted, setIsSubmitted] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm<ForgotPasswordForm>();

    const forgotPasswordMutation = useMutation({
        mutationFn: async (data: ForgotPasswordForm) => {
            // For now, just simulate success since email service may not be configured
            // In production, this would call: api.post('/api/auth/forgot-password', data)
            await new Promise(resolve => setTimeout(resolve, 1000));
            return { success: true };
        },
        onSuccess: () => {
            setIsSubmitted(true);
        },
    });

    const onSubmit = (data: ForgotPasswordForm) => {
        forgotPasswordMutation.mutate(data);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-primary-900 flex items-center justify-center p-4">
            {/* Back to Home Link */}
            <Link
                href="/"
                className="absolute top-6 left-6 flex items-center gap-2 text-dark-300 hover:text-white transition-colors"
            >
                <ArrowLeft className="w-5 h-5" />
                Back to Home
            </Link>

            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex items-center gap-3">
                        <Image src="/jarvis.svg" alt="JARVIS" width={56} height={56} />
                        <span className="text-2xl font-bold text-white">JARVIS</span>
                    </Link>
                </div>

                {/* Card */}
                <div className="bg-white dark:bg-dark-800 rounded-2xl shadow-xl p-8">
                    {!isSubmitted ? (
                        <>
                            <h1 className="text-2xl font-bold text-center text-dark-900 dark:text-white mb-2">
                                Forgot Password?
                            </h1>
                            <p className="text-center text-dark-500 dark:text-dark-400 mb-6">
                                Enter your email and we'll send you instructions to reset your password.
                            </p>

                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div>
                                    <label className="label">Email</label>
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
                                            className="input pl-10"
                                            placeholder="you@example.com"
                                        />
                                    </div>
                                    {errors.email && (
                                        <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>
                                    )}
                                </div>

                                {forgotPasswordMutation.isError && (
                                    <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
                                        <AlertCircle className="w-4 h-4" />
                                        Failed to send reset email. Please try again.
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={forgotPasswordMutation.isPending}
                                    className="w-full btn-primary py-3 disabled:opacity-50"
                                >
                                    {forgotPasswordMutation.isPending ? 'Sending...' : 'Send Reset Link'}
                                </button>
                            </form>
                        </>
                    ) : (
                        <div className="text-center py-4">
                            <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
                            </div>
                            <h2 className="text-xl font-bold text-dark-900 dark:text-white mb-2">
                                Check Your Email
                            </h2>
                            <p className="text-dark-500 dark:text-dark-400 mb-6">
                                If an account exists for that email, we've sent password reset instructions.
                            </p>
                            <p className="text-sm text-dark-400 dark:text-dark-500">
                                Didn't receive the email? Check your spam folder or{' '}
                                <button
                                    onClick={() => setIsSubmitted(false)}
                                    className="text-primary-600 hover:underline"
                                >
                                    try again
                                </button>
                            </p>
                        </div>
                    )}

                    <div className="mt-6 text-center">
                        <Link
                            href="/login"
                            className="text-sm text-primary-600 hover:text-primary-500 flex items-center justify-center gap-1"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to Login
                        </Link>
                    </div>
                </div>

                {/* Note about demo */}
                <p className="text-center text-dark-400 text-sm mt-6">
                    Note: Password reset emails require email service configuration.
                    <br />
                    Contact support if you need immediate assistance.
                </p>
            </div>
        </div>
    );
}
