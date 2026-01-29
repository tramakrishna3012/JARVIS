'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Plus, Download, Edit, Trash2, Wand2, Upload, FileUp, LayoutTemplate, X } from 'lucide-react';
import { resumesApi } from '../../../lib/api';
import ResumeEditor, { ResumeData } from '../../../components/resume/ResumeEditor';
import TemplateSelector from '../../../components/resume/TemplateSelector';

type CreateMode = 'scratch' | 'upload' | 'template' | null;

export default function ResumesPage() {
    const queryClient = useQueryClient();
    const [isEditorOpen, setIsEditorOpen] = useState(false);
    const [editingResume, setEditingResume] = useState<any>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [createMode, setCreateMode] = useState<CreateMode>(null);
    const [selectedTemplate, setSelectedTemplate] = useState('modern');
    const [selectedColor, setSelectedColor] = useState('#3B82F6');

    const { data: resumes, isLoading } = useQuery({
        queryKey: ['resumes'],
        queryFn: () => resumesApi.list().then(r => r.data),
    });

    const createResumeMutation = useMutation({
        mutationFn: (data: any) => resumesApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['resumes'] });
            setIsEditorOpen(false);
            setEditingResume(null);
        },
    });

    const updateResumeMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: any }) => resumesApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['resumes'] });
            setIsEditorOpen(false);
            setEditingResume(null);
        },
    });

    const deleteResumeMutation = useMutation({
        mutationFn: (id: string) => resumesApi.delete(id),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['resumes'] }),
    });

    const handleCreateNew = (mode: CreateMode) => {
        setCreateMode(mode);
        setShowCreateModal(false);

        if (mode === 'scratch' || mode === 'template') {
            setEditingResume(null);
            setIsEditorOpen(true);
        }
        // Upload mode would open a file picker - to be implemented
    };

    const handleEdit = (resume: any) => {
        setEditingResume(resume);
        setIsEditorOpen(true);
    };

    const handleSave = async (data: ResumeData) => {
        const payload = {
            name: data.personalInfo.fullName || 'Untitled Resume',
            content: data,
            template: data.template,
            theme_color: data.themeColor,
        };

        if (editingResume?.id) {
            await updateResumeMutation.mutateAsync({ id: editingResume.id, data: payload });
        } else {
            await createResumeMutation.mutateAsync(payload);
        }
    };

    const handleDownload = async (resumeId: string, format: 'pdf' | 'docx') => {
        try {
            const response = await resumesApi.download(resumeId, format);
            const blob = new Blob([response.data], {
                type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download failed:', error);
        }
    };

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this resume?')) {
            await deleteResumeMutation.mutateAsync(id);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-dark-900 dark:text-white">Resumes</h1>
                    <p className="text-dark-500 dark:text-dark-400 mt-1">
                        Create professional resumes with our AI-powered builder
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="btn-primary"
                    >
                        <Plus className="w-4 h-4 mr-2" />
                        Create Resume
                    </button>
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-12">
                    <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {resumes?.map((resume: any, index: number) => (
                        <motion.div
                            key={resume.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="card group hover:border-primary-500/50 transition-colors"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 rounded-lg bg-pink-500/10 flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-pink-500" />
                                </div>
                                <span className={`badge ${resume.is_base ? 'badge-info' : 'badge-success'}`}>
                                    {resume.is_base ? 'Base Resume' : 'Tailored'}
                                </span>
                            </div>

                            <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-1">
                                {resume.name}
                            </h3>
                            <p className="text-sm text-dark-500 dark:text-dark-400 mb-4 line-clamp-2">
                                {resume.target_job_title ? `Targeting: ${resume.target_job_title}` : 'General profile resume'}
                            </p>

                            <div className="flex items-center gap-2 pt-4 border-t border-dark-100 dark:border-dark-800">
                                <button
                                    onClick={() => handleEdit(resume)}
                                    className="btn-ghost flex-1 text-sm py-1.5"
                                >
                                    <Edit className="w-4 h-4 mr-2" />
                                    Edit
                                </button>
                                <button
                                    onClick={() => handleDownload(resume.id, 'pdf')}
                                    className="btn-ghost flex-1 text-sm py-1.5"
                                >
                                    <Download className="w-4 h-4 mr-2" />
                                    PDF
                                </button>
                                <button
                                    onClick={() => handleDelete(resume.id)}
                                    className="btn-ghost p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    ))}

                    {/* Add New Card */}
                    <motion.button
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        onClick={() => setShowCreateModal(true)}
                        className="card border-dashed border-2 flex flex-col items-center justify-center gap-4 text-dark-400 hover:text-primary-500 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-all min-h-[200px]"
                    >
                        <div className="w-12 h-12 rounded-full bg-dark-100 dark:bg-dark-800 flex items-center justify-center group-hover:bg-primary-100 dark:group-hover:bg-primary-900/30 transition-colors">
                            <Plus className="w-6 h-6" />
                        </div>
                        <span className="font-medium">Create Resume</span>
                    </motion.button>
                </div>
            )}

            {/* Create Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 bg-dark-900/80 backdrop-blur-sm flex items-center justify-center p-4"
                        onClick={() => setShowCreateModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-dark-800 rounded-2xl border border-dark-700 p-6 max-w-lg w-full"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white">Create New Resume</h2>
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5 text-dark-400" />
                                </button>
                            </div>

                            <div className="grid gap-4">
                                <button
                                    onClick={() => handleCreateNew('scratch')}
                                    className="flex items-center gap-4 p-4 bg-dark-700/50 hover:bg-dark-700 rounded-xl border border-dark-600 transition-colors text-left"
                                >
                                    <div className="w-12 h-12 rounded-lg bg-primary-500/20 flex items-center justify-center">
                                        <FileUp className="w-6 h-6 text-primary-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white">Start from Scratch</h3>
                                        <p className="text-sm text-dark-400">Create a new resume with our step-by-step editor</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCreateNew('template')}
                                    className="flex items-center gap-4 p-4 bg-dark-700/50 hover:bg-dark-700 rounded-xl border border-dark-600 transition-colors text-left"
                                >
                                    <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                                        <LayoutTemplate className="w-6 h-6 text-green-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white">Choose a Template</h3>
                                        <p className="text-sm text-dark-400">Start with a professional template design</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCreateNew('upload')}
                                    className="flex items-center gap-4 p-4 bg-dark-700/50 hover:bg-dark-700 rounded-xl border border-dark-600 transition-colors text-left"
                                >
                                    <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                                        <Upload className="w-6 h-6 text-purple-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white">Upload Existing Resume</h3>
                                        <p className="text-sm text-dark-400">Import and enhance your current resume</p>
                                    </div>
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Resume Editor */}
            <AnimatePresence>
                {isEditorOpen && (
                    <ResumeEditor
                        initialData={editingResume?.content}
                        onSave={handleSave}
                        onDownload={(format) => editingResume?.id && handleDownload(editingResume.id, format)}
                        onClose={() => {
                            setIsEditorOpen(false);
                            setEditingResume(null);
                        }}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}
