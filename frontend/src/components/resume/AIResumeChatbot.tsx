'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    MessageCircle,
    Send,
    Sparkles,
    X,
    Minimize2,
    Maximize2,
    Bot,
    User,
    Loader2,
    Wand2,
    Target,
    Award,
    Briefcase,
    FileText,
} from 'lucide-react';
import { resumesApi } from '@/lib/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    suggestions?: string[];
    action?: string;
    timestamp: Date;
}

interface AIResumeChatbotProps {
    resumeData: {
        personalInfo?: {
            fullName?: string;
            summary?: string;
        };
        experiences?: any[];
        skills?: string[];
        education?: any[];
    };
    onApplySuggestion?: (action: string, data: any) => void;
}

const quickActions = [
    { icon: Wand2, label: 'Improve my summary', prompt: 'Help me improve my professional summary' },
    { icon: Target, label: 'ATS tips', prompt: 'Give me tips to make my resume more ATS-friendly' },
    { icon: Award, label: 'Add achievements', prompt: 'Suggest impressive achievements I can add' },
    { icon: Briefcase, label: 'Better descriptions', prompt: 'Help me write better job descriptions' },
];

export default function AIResumeChatbot({ resumeData, onApplySuggestion }: AIResumeChatbotProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hi! I'm JARVIS, your AI resume assistant. I can help you improve your resume, suggest skills, optimize for ATS, and more. What would you like to work on?",
            suggestions: ['Improve my summary', 'Suggest skills', 'ATS optimization tips'],
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const getResumeContext = () => ({
        name: resumeData.personalInfo?.fullName || '',
        current_role: resumeData.experiences?.[0]?.position || '',
        years_experience: resumeData.experiences?.length || 0,
        skills: resumeData.skills || [],
        target_role: '',
    });

    const sendMessage = async (content: string) => {
        if (!content.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const chatHistory = messages.slice(-6).map((m) => ({
                role: m.role,
                content: m.content,
            }));

            const response = await resumesApi.aiChat(content, getResumeContext(), chatHistory);

            if (response.data.success) {
                const assistantMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: response.data.response,
                    suggestions: response.data.suggestions,
                    action: response.data.action,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, assistantMessage]);
            } else {
                throw new Error('AI response unsuccessful');
            }
        } catch (error: any) {
            console.error('Chat error:', error);

            let errorContent = "I'm having trouble connecting right now. Please try again in a moment.";

            // Check if it's an authentication error
            if (error?.response?.status === 401) {
                errorContent = "Your session may have expired. Please refresh the page or log in again.";
            } else if (error?.response?.status === 500) {
                errorContent = "The AI service is temporarily unavailable. Please try again later.";
            } else if (error?.message) {
                errorContent = `Error: ${error.message}`;
            }

            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: errorContent,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    if (!isOpen) {
        return (
            <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                whileHover={{ scale: 1.1 }}
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full shadow-lg flex items-center justify-center text-white z-50"
            >
                <MessageCircle className="w-6 h-6" />
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-dark-900 animate-pulse" />
            </motion.button>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.8 }}
            animate={{
                opacity: 1,
                y: 0,
                scale: 1,
                height: isMinimized ? 'auto' : 500,
            }}
            exit={{ opacity: 0, y: 100, scale: 0.8 }}
            className="fixed bottom-6 right-6 w-96 bg-dark-800 rounded-2xl shadow-2xl border border-dark-700 overflow-hidden z-50 flex flex-col"
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-dark-700 bg-gradient-to-r from-purple-600/20 to-pink-600/20">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">JARVIS AI</h3>
                        <p className="text-xs text-dark-400">Resume Assistant</p>
                    </div>
                </div>
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => setIsMinimized(!isMinimized)}
                        className="p-2 hover:bg-dark-700 rounded-lg transition-colors text-dark-400 hover:text-white"
                    >
                        {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                    </button>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="p-2 hover:bg-dark-700 rounded-lg transition-colors text-dark-400 hover:text-white"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <AnimatePresence>
                            {messages.map((message) => (
                                <motion.div
                                    key={message.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                                >
                                    <div
                                        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === 'user'
                                            ? 'bg-primary-600'
                                            : 'bg-gradient-to-r from-purple-600 to-pink-600'
                                            }`}
                                    >
                                        {message.role === 'user' ? (
                                            <User className="w-4 h-4 text-white" />
                                        ) : (
                                            <Bot className="w-4 h-4 text-white" />
                                        )}
                                    </div>
                                    <div
                                        className={`max-w-[80%] rounded-2xl px-4 py-2 ${message.role === 'user'
                                            ? 'bg-primary-600 text-white rounded-br-sm'
                                            : 'bg-dark-700 text-dark-100 rounded-bl-sm'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                        {message.suggestions && message.suggestions.length > 0 && (
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                {message.suggestions.map((suggestion, i) => (
                                                    <button
                                                        key={i}
                                                        onClick={() => sendMessage(suggestion)}
                                                        className="text-xs px-3 py-1 bg-dark-600 hover:bg-dark-500 rounded-full text-dark-200 transition-colors"
                                                    >
                                                        {suggestion}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {isLoading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex gap-3"
                            >
                                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                                    <Bot className="w-4 h-4 text-white" />
                                </div>
                                <div className="bg-dark-700 rounded-2xl rounded-bl-sm px-4 py-3">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Quick Actions */}
                    {messages.length <= 2 && (
                        <div className="px-4 pb-2">
                            <div className="flex flex-wrap gap-2">
                                {quickActions.map((action, i) => (
                                    <button
                                        key={i}
                                        onClick={() => sendMessage(action.prompt)}
                                        className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-full text-dark-300 hover:text-white transition-colors"
                                    >
                                        <action.icon className="w-3 h-3" />
                                        {action.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input */}
                    <div className="p-4 border-t border-dark-700">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask me anything about your resume..."
                                className="flex-1 bg-dark-700 border border-dark-600 rounded-xl px-4 py-2 text-sm text-white placeholder-dark-400 focus:outline-none focus:border-primary-500"
                                disabled={isLoading}
                            />
                            <button
                                onClick={() => sendMessage(input)}
                                disabled={!input.trim() || isLoading}
                                className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                    <Send className="w-4 h-4" />
                                )}
                            </button>
                        </div>
                    </div>
                </>
            )}
        </motion.div>
    );
}
