'use client';

import { motion } from 'framer-motion';
import { Check, Palette, Briefcase, GraduationCap, Code, Sparkles, Building2, Rocket } from 'lucide-react';

export interface Template {
    id: string;
    name: string;
    description: string;
    category: string;
    colors: string[];
    icon: React.ReactNode;
    features: string[];
}

const templates: Template[] = [
    {
        id: 'professional',
        name: 'Professional',
        description: 'Clean corporate layout, perfect for business roles',
        category: 'Business',
        colors: ['#1E40AF', '#1D4ED8', '#2563EB', '#3B82F6'],
        icon: <Briefcase className="w-5 h-5" />,
        features: ['ATS Optimized', 'Clean Layout', 'Traditional'],
    },
    {
        id: 'modern',
        name: 'Modern',
        description: 'Contemporary design with vibrant accents',
        category: 'General',
        colors: ['#059669', '#10B981', '#34D399', '#6EE7B7'],
        icon: <Sparkles className="w-5 h-5" />,
        features: ['Trendy', 'Eye-catching', 'Versatile'],
    },
    {
        id: 'tech',
        name: 'Tech Pro',
        description: 'Designed for developers and tech professionals',
        category: 'Technology',
        colors: ['#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD'],
        icon: <Code className="w-5 h-5" />,
        features: ['Skills Focus', 'Project Highlight', 'Compact'],
    },
    {
        id: 'executive',
        name: 'Executive',
        description: 'Elegant design for senior leadership positions',
        category: 'Leadership',
        colors: ['#0F172A', '#1E293B', '#334155', '#475569'],
        icon: <Building2 className="w-5 h-5" />,
        features: ['Premium', 'Authority', 'Sophisticated'],
    },
    {
        id: 'creative',
        name: 'Creative',
        description: 'Bold and artistic for design professionals',
        category: 'Design',
        colors: ['#DB2777', '#EC4899', '#F472B6', '#F9A8D4'],
        icon: <Rocket className="w-5 h-5" />,
        features: ['Unique', 'Colorful', 'Standout'],
    },
    {
        id: 'academic',
        name: 'Academic',
        description: 'Structured format for academic positions',
        category: 'Education',
        colors: ['#B45309', '#D97706', '#F59E0B', '#FBBF24'],
        icon: <GraduationCap className="w-5 h-5" />,
        features: ['Publications', 'Research', 'Detailed'],
    },
];

interface TemplateSelectorProps {
    selectedTemplate: string;
    selectedColor: string;
    onSelectTemplate: (templateId: string) => void;
    onSelectColor: (color: string) => void;
}

export default function TemplateSelector({
    selectedTemplate,
    selectedColor,
    onSelectTemplate,
    onSelectColor,
}: TemplateSelectorProps) {
    const currentTemplate = templates.find((t) => t.id === selectedTemplate) || templates[0];

    return (
        <div className="space-y-8">
            <div>
                <h3 className="text-lg font-semibold text-white mb-2">Choose Your Template</h3>
                <p className="text-dark-400 text-sm mb-6">Select a professional template that matches your industry</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {templates.map((template) => (
                        <motion.button
                            key={template.id}
                            onClick={() => {
                                onSelectTemplate(template.id);
                                onSelectColor(template.colors[0]);
                            }}
                            whileHover={{ scale: 1.02, y: -4 }}
                            whileTap={{ scale: 0.98 }}
                            className={`relative group rounded-xl overflow-hidden border-2 transition-all text-left ${selectedTemplate === template.id
                                ? 'border-primary-500 ring-2 ring-primary-500/30 bg-dark-800/80'
                                : 'border-dark-700 hover:border-dark-500 bg-dark-800/50'
                                }`}
                        >
                            {/* Template Preview */}
                            <div className="p-4">
                                <div className="flex items-start justify-between mb-3">
                                    <div
                                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                                        style={{ backgroundColor: `${template.colors[0]}20` }}
                                    >
                                        <div style={{ color: template.colors[0] }}>
                                            {template.icon}
                                        </div>
                                    </div>
                                    {selectedTemplate === template.id && (
                                        <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                                            <Check className="w-4 h-4 text-white" />
                                        </div>
                                    )}
                                </div>

                                <h4 className="font-semibold text-white mb-1">{template.name}</h4>
                                <p className="text-xs text-dark-400 mb-3">{template.description}</p>

                                {/* Features Tags */}
                                <div className="flex flex-wrap gap-1">
                                    {template.features.map((feature) => (
                                        <span
                                            key={feature}
                                            className="text-[10px] px-2 py-0.5 rounded-full bg-dark-700 text-dark-300"
                                        >
                                            {feature}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Preview Bar */}
                            <div
                                className="h-1.5 w-full"
                                style={{
                                    background: `linear-gradient(90deg, ${template.colors[0]}, ${template.colors[2]})`
                                }}
                            />
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Color Picker */}
            <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-700">
                <div className="flex items-center gap-2 mb-4">
                    <Palette className="w-5 h-5 text-dark-400" />
                    <h3 className="font-semibold text-white">Accent Color</h3>
                </div>
                <div className="flex flex-wrap gap-3">
                    {currentTemplate.colors.map((color) => (
                        <motion.button
                            key={color}
                            onClick={() => onSelectColor(color)}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            className={`w-10 h-10 rounded-full transition-all shadow-lg ${selectedColor === color
                                ? 'ring-2 ring-offset-2 ring-offset-dark-900 ring-white'
                                : 'hover:shadow-xl'
                                }`}
                            style={{ backgroundColor: color }}
                        />
                    ))}

                    {/* Custom Color Input */}
                    <label className="relative">
                        <motion.div
                            whileHover={{ scale: 1.1 }}
                            className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 via-green-500 to-blue-500 cursor-pointer flex items-center justify-center shadow-lg"
                        >
                            <span className="text-white text-lg font-bold">+</span>
                        </motion.div>
                        <input
                            type="color"
                            value={selectedColor}
                            onChange={(e) => onSelectColor(e.target.value)}
                            className="opacity-0 absolute w-0 h-0"
                        />
                    </label>
                </div>
                <p className="text-xs text-dark-500 mt-3">
                    Current: <span className="font-mono" style={{ color: selectedColor }}>{selectedColor}</span>
                </p>
            </div>
        </div>
    );
}

export { templates };
