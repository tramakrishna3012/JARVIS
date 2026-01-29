'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles,
    Wand2,
    User,
    Briefcase,
    GraduationCap,
    Target,
    Loader2,
    ChevronRight,
    ChevronLeft,
    Check,
    X,
    ArrowRight,
} from 'lucide-react';
import { resumesApi } from '../../lib/api';

interface AIResumeBuilderProps {
    onComplete: (resumeData: any) => void;
    onClose: () => void;
}

interface UserInput {
    name: string;
    email: string;
    phone: string;
    location: string;
    targetRole: string;
    industry: string;
    yearsExperience: string;
    currentRole: string;
    currentCompany: string;
    education: string;
    skills: string;
    achievements: string;
    linkedin: string;
    github: string;
    portfolio: string;
}

const initialInput: UserInput = {
    name: '',
    email: '',
    phone: '',
    location: '',
    targetRole: '',
    industry: 'Technology',
    yearsExperience: '',
    currentRole: '',
    currentCompany: '',
    education: '',
    skills: '',
    achievements: '',
    linkedin: '',
    github: '',
    portfolio: '',
};

const steps = [
    { id: 'basics', label: 'Basic Info', icon: User },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'education', label: 'Education & Skills', icon: GraduationCap },
    { id: 'target', label: 'Target Role', icon: Target },
];

export default function AIResumeBuilder({ onComplete, onClose }: AIResumeBuilderProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [input, setInput] = useState<UserInput>(initialInput);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const updateInput = (field: keyof UserInput, value: string) => {
        setInput(prev => ({ ...prev, [field]: value }));
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);

        try {
            // Prepare user input for AI
            const userInput = {
                name: input.name,
                email: input.email,
                phone: input.phone,
                location: input.location,
                target_role: input.targetRole,
                industry: input.industry,
                years_experience: input.yearsExperience,
                current_role: input.currentRole,
                current_company: input.currentCompany,
                education: input.education,
                skills: input.skills.split(',').map(s => s.trim()).filter(Boolean),
                achievements: input.achievements.split('\n').filter(Boolean),
                linkedin: input.linkedin,
                github: input.github,
                portfolio: input.portfolio,
            };

            const response = await resumesApi.aiBuild(userInput);

            if (response.data.success && response.data.resume) {
                // Add template and theme color defaults
                const resumeData = {
                    ...response.data.resume,
                    template: 'professional',
                    themeColor: '#1E40AF',
                };
                onComplete(resumeData);
            } else {
                setError('Failed to generate resume. Please try again.');
            }
        } catch (err: any) {
            console.error('AI generation error:', err);
            setError(err.response?.data?.detail || 'Failed to connect to AI service. Please try again.');
        } finally {
            setIsGenerating(false);
        }
    };

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            handleGenerate();
        }
    };

    const prevStep = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const isStepValid = () => {
        switch (currentStep) {
            case 0:
                return input.name.trim() !== '' && input.email.trim() !== '';
            case 1:
                return true; // Experience is optional
            case 2:
                return true; // Education is optional
            case 3:
                return input.targetRole.trim() !== '';
            default:
                return true;
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-dark-900/95 backdrop-blur-sm flex flex-col">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-dark-700 bg-dark-800/80">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-dark-400" />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">AI Resume Builder</h1>
                            <p className="text-sm text-dark-400">Let AI create your professional resume</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Step Navigation */}
            <nav className="flex items-center justify-center gap-2 px-6 py-4 border-b border-dark-700 bg-dark-800/50">
                {steps.map((step, index) => (
                    <button
                        key={step.id}
                        onClick={() => index <= currentStep && setCurrentStep(index)}
                        disabled={index > currentStep}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${currentStep === index
                                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                                : index < currentStep
                                    ? 'bg-green-600/20 text-green-400'
                                    : 'bg-dark-700 text-dark-400'
                            }`}
                    >
                        {index < currentStep ? (
                            <Check className="w-4 h-4" />
                        ) : (
                            <step.icon className="w-4 h-4" />
                        )}
                        <span className="hidden md:inline">{step.label}</span>
                    </button>
                ))}
            </nav>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-2xl mx-auto">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            {currentStep === 0 && (
                                <div className="space-y-6">
                                    <div className="text-center mb-8">
                                        <h2 className="text-2xl font-bold text-white mb-2">Let's start with your basics</h2>
                                        <p className="text-dark-400">Tell us your contact information</p>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Full Name *</label>
                                            <input
                                                type="text"
                                                value={input.name}
                                                onChange={(e) => updateInput('name', e.target.value)}
                                                placeholder="John Doe"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Email *</label>
                                            <input
                                                type="email"
                                                value={input.email}
                                                onChange={(e) => updateInput('email', e.target.value)}
                                                placeholder="john@example.com"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Phone</label>
                                            <input
                                                type="tel"
                                                value={input.phone}
                                                onChange={(e) => updateInput('phone', e.target.value)}
                                                placeholder="+91 98765 43210"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Location</label>
                                            <input
                                                type="text"
                                                value={input.location}
                                                onChange={(e) => updateInput('location', e.target.value)}
                                                placeholder="Mumbai, India"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">LinkedIn</label>
                                            <input
                                                type="text"
                                                value={input.linkedin}
                                                onChange={(e) => updateInput('linkedin', e.target.value)}
                                                placeholder="linkedin.com/in/johndoe"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">GitHub</label>
                                            <input
                                                type="text"
                                                value={input.github}
                                                onChange={(e) => updateInput('github', e.target.value)}
                                                placeholder="github.com/johndoe"
                                                className="input w-full"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentStep === 1 && (
                                <div className="space-y-6">
                                    <div className="text-center mb-8">
                                        <h2 className="text-2xl font-bold text-white mb-2">Your Work Experience</h2>
                                        <p className="text-dark-400">Tell us about your current/recent role</p>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Current/Recent Job Title</label>
                                            <input
                                                type="text"
                                                value={input.currentRole}
                                                onChange={(e) => updateInput('currentRole', e.target.value)}
                                                placeholder="Senior Software Engineer"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Company</label>
                                            <input
                                                type="text"
                                                value={input.currentCompany}
                                                onChange={(e) => updateInput('currentCompany', e.target.value)}
                                                placeholder="Tech Corp"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Years of Experience</label>
                                            <input
                                                type="text"
                                                value={input.yearsExperience}
                                                onChange={(e) => updateInput('yearsExperience', e.target.value)}
                                                placeholder="5"
                                                className="input w-full"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Industry</label>
                                            <select
                                                value={input.industry}
                                                onChange={(e) => updateInput('industry', e.target.value)}
                                                className="input w-full"
                                            >
                                                <option value="Technology">Technology</option>
                                                <option value="Finance">Finance</option>
                                                <option value="Healthcare">Healthcare</option>
                                                <option value="Education">Education</option>
                                                <option value="Retail">Retail</option>
                                                <option value="Manufacturing">Manufacturing</option>
                                                <option value="Consulting">Consulting</option>
                                                <option value="Other">Other</option>
                                            </select>
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Key Achievements (one per line)</label>
                                            <textarea
                                                value={input.achievements}
                                                onChange={(e) => updateInput('achievements', e.target.value)}
                                                placeholder="Led a team of 5 developers to deliver project 2 weeks ahead of schedule&#10;Improved system performance by 40%&#10;Reduced bug count by 60% through code reviews"
                                                rows={4}
                                                className="input w-full resize-none"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentStep === 2 && (
                                <div className="space-y-6">
                                    <div className="text-center mb-8">
                                        <h2 className="text-2xl font-bold text-white mb-2">Education & Skills</h2>
                                        <p className="text-dark-400">Tell us about your education and key skills</p>
                                    </div>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Education</label>
                                            <textarea
                                                value={input.education}
                                                onChange={(e) => updateInput('education', e.target.value)}
                                                placeholder="Bachelor of Technology in Computer Science, IIT Delhi, 2018"
                                                rows={3}
                                                className="input w-full resize-none"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Skills (comma separated)</label>
                                            <textarea
                                                value={input.skills}
                                                onChange={(e) => updateInput('skills', e.target.value)}
                                                placeholder="React, Node.js, Python, AWS, Docker, TypeScript, MongoDB, PostgreSQL"
                                                rows={3}
                                                className="input w-full resize-none"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Portfolio Website</label>
                                            <input
                                                type="text"
                                                value={input.portfolio}
                                                onChange={(e) => updateInput('portfolio', e.target.value)}
                                                placeholder="yourportfolio.com"
                                                className="input w-full"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentStep === 3 && (
                                <div className="space-y-6">
                                    <div className="text-center mb-8">
                                        <h2 className="text-2xl font-bold text-white mb-2">Target Role</h2>
                                        <p className="text-dark-400">What position are you applying for?</p>
                                    </div>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-dark-300 mb-2">Target Job Title *</label>
                                            <input
                                                type="text"
                                                value={input.targetRole}
                                                onChange={(e) => updateInput('targetRole', e.target.value)}
                                                placeholder="Full Stack Developer"
                                                className="input w-full text-lg"
                                            />
                                            <p className="text-xs text-dark-500 mt-2">
                                                The AI will optimize your resume for this role
                                            </p>
                                        </div>
                                    </div>

                                    {/* Summary of info */}
                                    <div className="mt-8 p-4 bg-dark-800 rounded-xl border border-dark-700">
                                        <h3 className="text-sm font-medium text-dark-400 mb-3">Resume Summary</h3>
                                        <div className="grid grid-cols-2 gap-3 text-sm">
                                            <div>
                                                <span className="text-dark-500">Name:</span>
                                                <span className="text-white ml-2">{input.name || '-'}</span>
                                            </div>
                                            <div>
                                                <span className="text-dark-500">Experience:</span>
                                                <span className="text-white ml-2">{input.yearsExperience || '0'} years</span>
                                            </div>
                                            <div>
                                                <span className="text-dark-500">Current Role:</span>
                                                <span className="text-white ml-2">{input.currentRole || '-'}</span>
                                            </div>
                                            <div>
                                                <span className="text-dark-500">Target:</span>
                                                <span className="text-primary-400 ml-2">{input.targetRole || '-'}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {error && (
                        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
                            {error}
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            <footer className="flex items-center justify-between px-6 py-4 border-t border-dark-700 bg-dark-800/80">
                <button
                    onClick={prevStep}
                    disabled={currentStep === 0 || isGenerating}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 text-white hover:bg-dark-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronLeft className="w-4 h-4" />
                    Back
                </button>
                <span className="text-dark-400">
                    Step {currentStep + 1} of {steps.length}
                </span>
                <button
                    onClick={nextStep}
                    disabled={!isStepValid() || isGenerating}
                    className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {isGenerating ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Generating with AI...
                        </>
                    ) : currentStep === steps.length - 1 ? (
                        <>
                            <Wand2 className="w-4 h-4" />
                            Generate Resume
                        </>
                    ) : (
                        <>
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </>
                    )}
                </button>
            </footer>
        </div>
    );
}
