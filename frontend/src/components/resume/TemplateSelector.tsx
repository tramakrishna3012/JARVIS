'use client';

import { motion } from 'framer-motion';
import { Check, Palette } from 'lucide-react';

export interface Template {
    id: string;
    name: string;
    description: string;
    preview: string;
    colors: string[];
}

const templates: Template[] = [
    {
        id: 'modern',
        name: 'Modern',
        description: 'Clean and contemporary design with bold headers',
        preview: '/templates/modern.png',
        colors: ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'],
    },
    {
        id: 'classic',
        name: 'Classic',
        description: 'Traditional professional layout, ideal for corporate roles',
        preview: '/templates/classic.png',
        colors: ['#1F2937', '#374151', '#4B5563', '#6B7280'],
    },
    {
        id: 'creative',
        name: 'Creative',
        description: 'Stylish design for designers and creative professionals',
        preview: '/templates/creative.png',
        colors: ['#EC4899', '#F43F5E', '#F97316', '#EAB308'],
    },
    {
        id: 'minimal',
        name: 'Minimal',
        description: 'Simple and elegant with focus on content',
        preview: '/templates/minimal.png',
        colors: ['#18181B', '#27272A', '#3F3F46', '#52525B'],
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
                <h3 className="text-lg font-semibold text-white mb-4">Choose a Template</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {templates.map((template) => (
                        <motion.button
                            key={template.id}
                            onClick={() => onSelectTemplate(template.id)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`relative group rounded-xl overflow-hidden border-2 transition-all ${selectedTemplate === template.id
                                    ? 'border-primary-500 ring-2 ring-primary-500/30'
                                    : 'border-dark-700 hover:border-dark-500'
                                }`}
                        >
                            {/* Preview Background */}
                            <div className="aspect-[3/4] bg-gradient-to-br from-dark-700 to-dark-800 flex items-center justify-center">
                                <div className="w-3/4 h-3/4 bg-white rounded shadow-lg flex flex-col p-2">
                                    <div
                                        className="h-3 rounded-full mb-2"
                                        style={{ backgroundColor: template.colors[0] }}
                                    />
                                    <div className="flex-1 space-y-1">
                                        <div className="h-2 bg-gray-200 rounded w-full" />
                                        <div className="h-2 bg-gray-200 rounded w-3/4" />
                                        <div className="h-2 bg-gray-200 rounded w-1/2" />
                                    </div>
                                </div>
                            </div>

                            {/* Selected Indicator */}
                            {selectedTemplate === template.id && (
                                <div className="absolute top-2 right-2 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                                    <Check className="w-4 h-4 text-white" />
                                </div>
                            )}

                            {/* Template Info */}
                            <div className="p-3 bg-dark-800">
                                <h4 className="font-medium text-white text-sm">{template.name}</h4>
                                <p className="text-xs text-dark-400 line-clamp-1">{template.description}</p>
                            </div>
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Color Picker */}
            <div>
                <div className="flex items-center gap-2 mb-4">
                    <Palette className="w-5 h-5 text-dark-400" />
                    <h3 className="text-lg font-semibold text-white">Accent Color</h3>
                </div>
                <div className="flex flex-wrap gap-3">
                    {currentTemplate.colors.map((color) => (
                        <button
                            key={color}
                            onClick={() => onSelectColor(color)}
                            className={`w-10 h-10 rounded-full transition-all ${selectedColor === color
                                    ? 'ring-2 ring-offset-2 ring-offset-dark-900 ring-white scale-110'
                                    : 'hover:scale-105'
                                }`}
                            style={{ backgroundColor: color }}
                        />
                    ))}
                    {/* Custom Color Input */}
                    <label className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 via-green-500 to-blue-500 cursor-pointer flex items-center justify-center hover:scale-105 transition-transform">
                        <input
                            type="color"
                            value={selectedColor}
                            onChange={(e) => onSelectColor(e.target.value)}
                            className="opacity-0 absolute w-0 h-0"
                        />
                        <span className="text-white text-xs font-bold">+</span>
                    </label>
                </div>
            </div>
        </div>
    );
}

export { templates };
