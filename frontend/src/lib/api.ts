/**
 * API Client for JARVIS Backend
 * Optimized with timeout, interceptors, and error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with optimized settings
const api: AxiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    // Timeout after 15 seconds to prevent hanging
    timeout: 15000,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && originalRequest) {
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    const { data } = await axios.post(`${API_URL}/api/auth/refresh`, {
                        refresh_token: refreshToken,
                    });

                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);

                    originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
                    return api(originalRequest);
                } catch {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                }
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authApi = {
    register: (email: string, password: string) =>
        api.post('/api/auth/register', { email, password }),

    login: (email: string, password: string) =>
        api.post('/api/auth/login', { email, password }),

    me: () => api.get('/api/auth/me'),

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
};

// Profile API
export const profileApi = {
    get: () => api.get('/api/profiles/me'),
    update: (data: any) => api.put('/api/profiles/me', data),
    addSkill: (data: any) => api.post('/api/profiles/me/skills', data),
    deleteSkill: (id: number) => api.delete(`/api/profiles/me/skills/${id}`),
    addEducation: (data: any) => api.post('/api/profiles/me/education', data),
    deleteEducation: (id: number) => api.delete(`/api/profiles/me/education/${id}`),
    addExperience: (data: any) => api.post('/api/profiles/me/experience', data),
    deleteExperience: (id: number) => api.delete(`/api/profiles/me/experience/${id}`),
};

// Jobs API
export const jobsApi = {
    list: (params?: any) => api.get('/api/jobs', { params }),
    get: (id: number) => api.get(`/api/jobs/${id}`),
    create: (data: any) => api.post('/api/jobs', data),
    update: (id: number, data: any) => api.put(`/api/jobs/${id}`, data),
    delete: (id: number) => api.delete(`/api/jobs/${id}`),
    discover: (data: any) => api.post('/api/jobs/discover', data),
};

export const resumesApi = {
    list: () => api.get('/api/resumes'),
    get: (id: number) => api.get(`/api/resumes/${id}`),
    create: (data: any) => api.post('/api/resumes', data),
    generate: (data: any) => api.post('/api/resumes/generate', data),
    update: (id: number | string, data: any) => api.put(`/api/resumes/${id}`, data),
    download: (id: number | string, format: 'pdf' | 'docx' = 'pdf') =>
        api.get(`/api/resumes/${id}/download`, { params: { format }, responseType: 'blob' }),
    analyze: (id: number) => api.post(`/api/resumes/${id}/analyze`),
    delete: (id: number | string) => api.delete(`/api/resumes/${id}`),
};

// Applications API
export const applicationsApi = {
    list: (params?: any) => api.get('/api/applications', { params }),
    get: (id: number) => api.get(`/api/applications/${id}`),
    create: (data: any) => api.post('/api/applications', data),
    apply: (data: any) => api.post('/api/applications/apply', data),
    update: (id: number, data: any) => api.put(`/api/applications/${id}`, data),
    stats: () => api.get('/api/applications/stats'),
    delete: (id: number) => api.delete(`/api/applications/${id}`),
};

// Referrals API
export const referralsApi = {
    listConnections: (params?: any) => api.get('/api/referrals/connections', { params }),
    searchConnections: (data: any) => api.post('/api/referrals/connections/search', data),
    syncConnections: () => api.post('/api/referrals/connections/sync'),
    list: (params?: any) => api.get('/api/referrals', { params }),
    create: (data: any) => api.post('/api/referrals', data),
    generateMessage: (id: number, data: any) => api.post(`/api/referrals/${id}/draft`, data),
    send: (id: number, data: any) => api.post(`/api/referrals/${id}/send`, data),
    update: (id: number, data: any) => api.put(`/api/referrals/${id}`, data),
};

// Emails API
export const emailsApi = {
    list: (params?: any) => api.get('/api/emails', { params }),
    inbox: (params?: any) => api.get('/api/emails/inbox', { params }),
    sent: (params?: any) => api.get('/api/emails/sent', { params }),
    get: (id: number) => api.get(`/api/emails/${id}`),
    send: (data: any) => api.post('/api/emails/send', data),
    reply: (id: number, data: any) => api.post(`/api/emails/${id}/reply`, data),
    sync: () => api.post('/api/emails/sync'),
    stats: () => api.get('/api/emails/stats'),
    delete: (id: number) => api.delete(`/api/emails/${id}`),
};

export default api;
