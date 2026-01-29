'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    User,
    Briefcase,
    GraduationCap,
    Wrench,
    Award,
    FileText,
    ChevronLeft,
    ChevronRight,
    Save,
    Download,
    Eye,
    Plus,
    Trash2,
    X,
} from 'lucide-react';

// Types for Resume Data
export interface PersonalInfo {
    fullName: string;
    email: string;
    phone: string;
    location: string;
    linkedin?: string;
    website?: string;
    summary: string;
}

export interface Experience {
    id: string;
    company: string;
    position: string;
    location: string;
    startDate: string;
    endDate: string;
    current: boolean;
    description: string;
    highlights: string[];
}

export interface Education {
    id: string;
    institution: string;
    degree: string;
    field: string;
    location: string;
    startDate: string;
    endDate: string;
    gpa?: string;
}

export interface ResumeData {
    personalInfo: PersonalInfo;
    experiences: Experience[];
    education: Education[];
    skills: string[];
    certifications: string[];
    template: string;
    themeColor: string;
}

const defaultResumeData: ResumeData = {
    personalInfo: {
        fullName: '',
        email: '',
        phone: '',
        location: '',
        linkedin: '',
        website: '',
        summary: '',
    },
    experiences: [],
    education: [],
    skills: [],
    certifications: [],
    template: 'modern',
    themeColor: '#3B82F6',
};

interface ResumeEditorProps {
    initialData?: Partial<ResumeData>;
    onSave?: (data: ResumeData) => void;
    onDownload?: (format: 'pdf' | 'docx') => void;
    onClose?: () => void;
}

const steps = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'skills', label: 'Skills', icon: Wrench },
    { id: 'preview', label: 'Preview', icon: Eye },
];

export default function ResumeEditor({
    initialData,
    onSave,
    onDownload,
    onClose,
}: ResumeEditorProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [data, setData] = useState<ResumeData>({
        ...defaultResumeData,
        ...initialData,
    });
    const [isSaving, setIsSaving] = useState(false);

    const updatePersonalInfo = (field: keyof PersonalInfo, value: string) => {
        setData((prev) => ({
            ...prev,
            personalInfo: { ...prev.personalInfo, [field]: value },
        }));
    };

    const addExperience = () => {
        const newExp: Experience = {
            id: Date.now().toString(),
            company: '',
            position: '',
            location: '',
            startDate: '',
            endDate: '',
            current: false,
            description: '',
            highlights: [],
        };
        setData((prev) => ({
            ...prev,
            experiences: [...prev.experiences, newExp],
        }));
    };

    const updateExperience = (id: string, field: keyof Experience, value: any) => {
        setData((prev) => ({
            ...prev,
            experiences: prev.experiences.map((exp) =>
                exp.id === id ? { ...exp, [field]: value } : exp
            ),
        }));
    };

    const removeExperience = (id: string) => {
        setData((prev) => ({
            ...prev,
            experiences: prev.experiences.filter((exp) => exp.id !== id),
        }));
    };

    const addEducation = () => {
        const newEdu: Education = {
            id: Date.now().toString(),
            institution: '',
            degree: '',
            field: '',
            location: '',
            startDate: '',
            endDate: '',
        };
        setData((prev) => ({
            ...prev,
            education: [...prev.education, newEdu],
        }));
    };

    const updateEducation = (id: string, field: keyof Education, value: string) => {
        setData((prev) => ({
            ...prev,
            education: prev.education.map((edu) =>
                edu.id === id ? { ...edu, [field]: value } : edu
            ),
        }));
    };

    const removeEducation = (id: string) => {
        setData((prev) => ({
            ...prev,
            education: prev.education.filter((edu) => edu.id !== id),
        }));
    };

    const addSkill = (skill: string) => {
        if (skill.trim() && !data.skills.includes(skill.trim())) {
            setData((prev) => ({
                ...prev,
                skills: [...prev.skills, skill.trim()],
            }));
        }
    };

    const removeSkill = (skill: string) => {
        setData((prev) => ({
            ...prev,
            skills: prev.skills.filter((s) => s !== skill),
        }));
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await onSave?.(data);
        } finally {
            setIsSaving(false);
        }
    };

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
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
                    <h1 className="text-xl font-bold text-white">Resume Editor</h1>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="btn-secondary flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" />
                        {isSaving ? 'Saving...' : 'Save Draft'}
                    </button>
                    <button
                        onClick={() => onDownload?.('pdf')}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Download className="w-4 h-4" />
                        Download PDF
                    </button>
                </div>
            </header>

            {/* Step Navigation */}
            <nav className="flex items-center justify-center gap-2 px-6 py-4 border-b border-dark-700 bg-dark-800/50">
                {steps.map((step, index) => (
                    <button
                        key={step.id}
                        onClick={() => setCurrentStep(index)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${currentStep === index
                                ? 'bg-primary-600 text-white'
                                : index < currentStep
                                    ? 'bg-green-600/20 text-green-400'
                                    : 'bg-dark-700 text-dark-400 hover:text-white'
                            }`}
                    >
                        <step.icon className="w-4 h-4" />
                        <span className="hidden md:inline">{step.label}</span>
                    </button>
                ))}
            </nav>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden flex">
                {/* Editor Panel */}
                <div className="flex-1 overflow-y-auto p-6">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="max-w-2xl mx-auto"
                        >
                            {currentStep === 0 && (
                                <PersonalInfoForm
                                    data={data.personalInfo}
                                    onChange={updatePersonalInfo}
                                />
                            )}
                            {currentStep === 1 && (
                                <ExperienceForm
                                    experiences={data.experiences}
                                    onAdd={addExperience}
                                    onUpdate={updateExperience}
                                    onRemove={removeExperience}
                                />
                            )}
                            {currentStep === 2 && (
                                <EducationForm
                                    education={data.education}
                                    onAdd={addEducation}
                                    onUpdate={updateEducation}
                                    onRemove={removeEducation}
                                />
                            )}
                            {currentStep === 3 && (
                                <SkillsForm
                                    skills={data.skills}
                                    onAdd={addSkill}
                                    onRemove={removeSkill}
                                />
                            )}
                            {currentStep === 4 && (
                                <ResumePreview data={data} />
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Live Preview Panel (visible on larger screens) */}
                {currentStep < 4 && (
                    <div className="hidden lg:block w-[450px] border-l border-dark-700 bg-dark-800/30 overflow-y-auto p-4">
                        <div className="sticky top-0 mb-4 pb-2 border-b border-dark-700">
                            <h3 className="text-sm font-medium text-dark-400">Live Preview</h3>
                        </div>
                        <div className="transform scale-[0.6] origin-top">
                            <ResumePreview data={data} />
                        </div>
                    </div>
                )}
            </div>

            {/* Footer Navigation */}
            <footer className="flex items-center justify-between px-6 py-4 border-t border-dark-700 bg-dark-800/80">
                <button
                    onClick={prevStep}
                    disabled={currentStep === 0}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 text-white hover:bg-dark-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                </button>
                <span className="text-dark-400">
                    Step {currentStep + 1} of {steps.length}
                </span>
                <button
                    onClick={nextStep}
                    disabled={currentStep === steps.length - 1}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    Next
                    <ChevronRight className="w-4 h-4" />
                </button>
            </footer>
        </div>
    );
}

// --- Sub-Components ---

function PersonalInfoForm({
    data,
    onChange,
}: {
    data: PersonalInfo;
    onChange: (field: keyof PersonalInfo, value: string) => void;
}) {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-dark-300 mb-2">Full Name</label>
                    <input
                        type="text"
                        value={data.fullName}
                        onChange={(e) => onChange('fullName', e.target.value)}
                        placeholder="John Doe"
                        className="input w-full"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">Email</label>
                    <input
                        type="email"
                        value={data.email}
                        onChange={(e) => onChange('email', e.target.value)}
                        placeholder="john@example.com"
                        className="input w-full"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">Phone</label>
                    <input
                        type="tel"
                        value={data.phone}
                        onChange={(e) => onChange('phone', e.target.value)}
                        placeholder="+1 (555) 123-4567"
                        className="input w-full"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">Location</label>
                    <input
                        type="text"
                        value={data.location}
                        onChange={(e) => onChange('location', e.target.value)}
                        placeholder="San Francisco, CA"
                        className="input w-full"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">LinkedIn (optional)</label>
                    <input
                        type="url"
                        value={data.linkedin || ''}
                        onChange={(e) => onChange('linkedin', e.target.value)}
                        placeholder="linkedin.com/in/johndoe"
                        className="input w-full"
                    />
                </div>
                <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-dark-300 mb-2">Professional Summary</label>
                    <textarea
                        value={data.summary}
                        onChange={(e) => onChange('summary', e.target.value)}
                        placeholder="A brief summary of your professional background and goals..."
                        rows={4}
                        className="input w-full resize-none"
                    />
                </div>
            </div>
        </div>
    );
}

function ExperienceForm({
    experiences,
    onAdd,
    onUpdate,
    onRemove,
}: {
    experiences: Experience[];
    onAdd: () => void;
    onUpdate: (id: string, field: keyof Experience, value: any) => void;
    onRemove: (id: string) => void;
}) {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Work Experience</h2>
                <button onClick={onAdd} className="btn-secondary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Experience
                </button>
            </div>

            {experiences.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-dark-700 rounded-xl">
                    <Briefcase className="w-12 h-12 text-dark-500 mx-auto mb-4" />
                    <p className="text-dark-400">No experience added yet</p>
                    <button onClick={onAdd} className="text-primary-400 hover:text-primary-300 mt-2">
                        Add your first experience
                    </button>
                </div>
            ) : (
                <div className="space-y-6">
                    {experiences.map((exp, index) => (
                        <motion.div
                            key={exp.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-4 bg-dark-800 rounded-xl border border-dark-700"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-medium text-white">Experience {index + 1}</h3>
                                <button
                                    onClick={() => onRemove(exp.id)}
                                    className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Company</label>
                                    <input
                                        type="text"
                                        value={exp.company}
                                        onChange={(e) => onUpdate(exp.id, 'company', e.target.value)}
                                        placeholder="Company Name"
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Position</label>
                                    <input
                                        type="text"
                                        value={exp.position}
                                        onChange={(e) => onUpdate(exp.id, 'position', e.target.value)}
                                        placeholder="Job Title"
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Start Date</label>
                                    <input
                                        type="month"
                                        value={exp.startDate}
                                        onChange={(e) => onUpdate(exp.id, 'startDate', e.target.value)}
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">End Date</label>
                                    <input
                                        type="month"
                                        value={exp.endDate}
                                        onChange={(e) => onUpdate(exp.id, 'endDate', e.target.value)}
                                        disabled={exp.current}
                                        className="input w-full disabled:opacity-50"
                                    />
                                </div>
                                <div className="md:col-span-2 flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id={`current-${exp.id}`}
                                        checked={exp.current}
                                        onChange={(e) => onUpdate(exp.id, 'current', e.target.checked)}
                                        className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-600"
                                    />
                                    <label htmlFor={`current-${exp.id}`} className="text-sm text-dark-300">
                                        I currently work here
                                    </label>
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Description</label>
                                    <textarea
                                        value={exp.description}
                                        onChange={(e) => onUpdate(exp.id, 'description', e.target.value)}
                                        placeholder="Describe your responsibilities and achievements..."
                                        rows={3}
                                        className="input w-full resize-none"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}

function EducationForm({
    education,
    onAdd,
    onUpdate,
    onRemove,
}: {
    education: Education[];
    onAdd: () => void;
    onUpdate: (id: string, field: keyof Education, value: string) => void;
    onRemove: (id: string) => void;
}) {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Education</h2>
                <button onClick={onAdd} className="btn-secondary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Education
                </button>
            </div>

            {education.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-dark-700 rounded-xl">
                    <GraduationCap className="w-12 h-12 text-dark-500 mx-auto mb-4" />
                    <p className="text-dark-400">No education added yet</p>
                    <button onClick={onAdd} className="text-primary-400 hover:text-primary-300 mt-2">
                        Add your education
                    </button>
                </div>
            ) : (
                <div className="space-y-6">
                    {education.map((edu, index) => (
                        <motion.div
                            key={edu.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-4 bg-dark-800 rounded-xl border border-dark-700"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-medium text-white">Education {index + 1}</h3>
                                <button
                                    onClick={() => onRemove(edu.id)}
                                    className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Institution</label>
                                    <input
                                        type="text"
                                        value={edu.institution}
                                        onChange={(e) => onUpdate(edu.id, 'institution', e.target.value)}
                                        placeholder="University or School Name"
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Degree</label>
                                    <input
                                        type="text"
                                        value={edu.degree}
                                        onChange={(e) => onUpdate(edu.id, 'degree', e.target.value)}
                                        placeholder="Bachelor's, Master's, etc."
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Field of Study</label>
                                    <input
                                        type="text"
                                        value={edu.field}
                                        onChange={(e) => onUpdate(edu.id, 'field', e.target.value)}
                                        placeholder="Computer Science, Business, etc."
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">Start Date</label>
                                    <input
                                        type="month"
                                        value={edu.startDate}
                                        onChange={(e) => onUpdate(edu.id, 'startDate', e.target.value)}
                                        className="input w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-dark-300 mb-2">End Date</label>
                                    <input
                                        type="month"
                                        value={edu.endDate}
                                        onChange={(e) => onUpdate(edu.id, 'endDate', e.target.value)}
                                        className="input w-full"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}

function SkillsForm({
    skills,
    onAdd,
    onRemove,
}: {
    skills: string[];
    onAdd: (skill: string) => void;
    onRemove: (skill: string) => void;
}) {
    const [newSkill, setNewSkill] = useState('');

    const handleAdd = () => {
        if (newSkill.trim()) {
            onAdd(newSkill);
            setNewSkill('');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAdd();
        }
    };

    const suggestedSkills = [
        'JavaScript', 'TypeScript', 'React', 'Node.js', 'Python',
        'AWS', 'Docker', 'Kubernetes', 'SQL', 'Git',
        'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
    ].filter(s => !skills.includes(s));

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Skills</h2>

            <div className="flex gap-2">
                <input
                    type="text"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Add a skill..."
                    className="input flex-1"
                />
                <button onClick={handleAdd} className="btn-primary">
                    <Plus className="w-4 h-4" />
                </button>
            </div>

            {skills.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {skills.map((skill) => (
                        <motion.span
                            key={skill}
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="px-3 py-1.5 bg-primary-600/20 text-primary-400 rounded-full text-sm flex items-center gap-2"
                        >
                            {skill}
                            <button
                                onClick={() => onRemove(skill)}
                                className="hover:text-red-400 transition-colors"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </motion.span>
                    ))}
                </div>
            )}

            {suggestedSkills.length > 0 && (
                <div>
                    <p className="text-sm text-dark-400 mb-2">Suggested Skills:</p>
                    <div className="flex flex-wrap gap-2">
                        {suggestedSkills.slice(0, 8).map((skill) => (
                            <button
                                key={skill}
                                onClick={() => onAdd(skill)}
                                className="px-3 py-1.5 bg-dark-700 text-dark-300 rounded-full text-sm hover:bg-dark-600 hover:text-white transition-colors"
                            >
                                + {skill}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function ResumePreview({ data }: { data: ResumeData }) {
    const formatDate = (dateStr: string) => {
        if (!dateStr) return '';
        const date = new Date(dateStr + '-01');
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    };

    return (
        <div className="bg-white text-gray-900 p-8 rounded-lg shadow-xl min-h-[800px]" style={{ width: '612px' }}>
            {/* Header */}
            <div className="text-center mb-6 pb-4 border-b-2" style={{ borderColor: data.themeColor }}>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {data.personalInfo.fullName || 'Your Name'}
                </h1>
                <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
                    {data.personalInfo.email && <span>{data.personalInfo.email}</span>}
                    {data.personalInfo.phone && <span>{data.personalInfo.phone}</span>}
                    {data.personalInfo.location && <span>{data.personalInfo.location}</span>}
                </div>
                {data.personalInfo.linkedin && (
                    <div className="text-sm text-blue-600 mt-1">{data.personalInfo.linkedin}</div>
                )}
            </div>

            {/* Summary */}
            {data.personalInfo.summary && (
                <div className="mb-6">
                    <h2 className="text-lg font-bold mb-2" style={{ color: data.themeColor }}>
                        Professional Summary
                    </h2>
                    <p className="text-sm text-gray-700 leading-relaxed">{data.personalInfo.summary}</p>
                </div>
            )}

            {/* Experience */}
            {data.experiences.length > 0 && (
                <div className="mb-6">
                    <h2 className="text-lg font-bold mb-3" style={{ color: data.themeColor }}>
                        Experience
                    </h2>
                    <div className="space-y-4">
                        {data.experiences.map((exp) => (
                            <div key={exp.id}>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="font-semibold text-gray-900">{exp.position || 'Position'}</h3>
                                        <p className="text-sm text-gray-600">{exp.company || 'Company'}</p>
                                    </div>
                                    <div className="text-sm text-gray-500 text-right">
                                        {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                                    </div>
                                </div>
                                {exp.description && (
                                    <p className="text-sm text-gray-700 mt-2">{exp.description}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Education */}
            {data.education.length > 0 && (
                <div className="mb-6">
                    <h2 className="text-lg font-bold mb-3" style={{ color: data.themeColor }}>
                        Education
                    </h2>
                    <div className="space-y-3">
                        {data.education.map((edu) => (
                            <div key={edu.id} className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-semibold text-gray-900">
                                        {edu.degree} {edu.field && `in ${edu.field}`}
                                    </h3>
                                    <p className="text-sm text-gray-600">{edu.institution || 'Institution'}</p>
                                </div>
                                <div className="text-sm text-gray-500">
                                    {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Skills */}
            {data.skills.length > 0 && (
                <div>
                    <h2 className="text-lg font-bold mb-3" style={{ color: data.themeColor }}>
                        Skills
                    </h2>
                    <div className="flex flex-wrap gap-2">
                        {data.skills.map((skill) => (
                            <span
                                key={skill}
                                className="px-2 py-1 text-sm rounded"
                                style={{ backgroundColor: `${data.themeColor}20`, color: data.themeColor }}
                            >
                                {skill}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
