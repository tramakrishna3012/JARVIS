/**
 * TypeScript type definitions for JARVIS
 */

// User & Auth
export interface User {
    id: number;
    email: string;
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
    last_login: string | null;
}

export interface AuthResponse {
    user: User;
    tokens: {
        access_token: string;
        refresh_token: string;
        token_type: string;
        expires_in: number;
    };
}

// Profile
export interface Skill {
    id: number;
    name: string;
    category: string | null;
    proficiency: string;
    years_used: number | null;
}

export interface Education {
    id: number;
    institution: string;
    degree: string;
    field_of_study: string | null;
    grade: string | null;
    start_date: string | null;
    end_date: string | null;
    is_current: boolean;
    description: string | null;
}

export interface Experience {
    id: number;
    company: string;
    title: string;
    location: string | null;
    employment_type: string | null;
    start_date: string;
    end_date: string | null;
    is_current: boolean;
    description: string | null;
    technologies: string[];
}

export interface Profile {
    id: number;
    user_id: number;
    first_name: string;
    last_name: string;
    phone: string | null;
    linkedin_url: string | null;
    github_url: string | null;
    portfolio_url: string | null;
    headline: string | null;
    summary: string | null;

    // Job preferences
    preferred_job_countries: string[];
    preferred_job_cities: string[];
    work_authorization: Record<string, string>;
    relocation_willing: boolean;
    remote_preference: 'remote' | 'hybrid' | 'onsite' | 'any';

    // Experience & availability
    years_of_experience: number;
    current_company: string | null;
    current_title: string | null;
    min_salary_expectation: number | null;
    preferred_currency: string;
    notice_period_days: number;
    available_from: string | null;

    // Related data
    skills: Skill[];
    education: Education[];
    experience: Experience[];

    created_at: string;
    updated_at: string;
}

// Jobs
export type JobStatus =
    | 'discovered'
    | 'interested'
    | 'applied'
    | 'interviewing'
    | 'offered'
    | 'rejected'
    | 'withdrawn'
    | 'expired';

export type JobSource =
    | 'linkedin'
    | 'naukri'
    | 'company_career'
    | 'email'
    | 'whatsapp'
    | 'instagram'
    | 'referral'
    | 'other';

export interface Job {
    id: number;
    title: string;
    company: string;
    description: string | null;
    requirements: string | null;
    location: string | null;
    country: string | null;
    city: string | null;
    is_remote: boolean;
    work_type: string | null;
    salary_min: number | null;
    salary_max: number | null;
    salary_currency: string;
    employment_type: string | null;
    experience_required: string | null;
    experience_min_years: number | null;
    experience_max_years: number | null;
    source: JobSource;
    source_url: string | null;
    apply_url: string | null;
    required_skills: string[];
    nice_to_have_skills: string[];
    relevance_score: number;
    skill_match_score: number;
    experience_match_score: number;
    location_match_score: number;
    status: JobStatus;
    is_duplicate: boolean;
    posted_date: string | null;
    deadline: string | null;
    discovered_at: string;
}

// Resume
export interface Resume {
    id: number;
    user_id: number;
    name: string;
    version: number;
    is_master: boolean;
    target_job_id: number | null;
    target_job_title: string | null;
    target_company: string | null;
    content: Record<string, any>;
    pdf_url: string | null;
    ats_score: number | null;
    ats_feedback: Record<string, any> | null;
    keywords_included: string[];
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

// Application
export type ApplicationStatus =
    | 'pending'
    | 'submitted'
    | 'viewed'
    | 'screening'
    | 'interview_scheduled'
    | 'interviewing'
    | 'offered'
    | 'accepted'
    | 'rejected'
    | 'withdrawn'
    | 'failed';

export interface ScreeningQuestion {
    question: string;
    answer: string;
    auto_answered: boolean;
}

export interface InterviewRound {
    round: number;
    type: string;
    date: string | null;
    interviewer: string | null;
    feedback: string | null;
    status: string;
}

export interface Application {
    id: number;
    user_id: number;
    job_id: number | null;
    resume_id: number | null;
    status: ApplicationStatus;
    method: string;
    submitted_at: string | null;
    confirmation_number: string | null;
    cover_letter: string | null;
    screening_questions: ScreeningQuestion[];
    interview_rounds: InterviewRound[];
    response_received: boolean;
    response_date: string | null;
    offer_salary: number | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
}

export interface ApplicationStats {
    total: number;
    pending: number;
    submitted: number;
    interviewing: number;
    offered: number;
    rejected: number;
    acceptance_rate: number;
}

// Referral
export type ReferralStatus =
    | 'draft'
    | 'pending'
    | 'accepted'
    | 'ignored'
    | 'declined'
    | 'referred'
    | 'follow_up';

export interface Connection {
    id: number;
    name: string;
    first_name: string | null;
    last_name: string | null;
    email: string | null;
    linkedin_url: string | null;
    headline: string | null;
    current_company: string | null;
    current_title: string | null;
    location: string | null;
    is_recruiter: boolean;
    is_hiring_manager: boolean;
    connection_degree: number;
    synced_at: string;
}

export interface Referral {
    id: number;
    user_id: number;
    job_id: number | null;
    connection_id: number | null;
    target_company: string;
    target_job_title: string | null;
    target_job_url: string | null;
    connection_name: string | null;
    connection_title: string | null;
    message_draft: string | null;
    message_sent: string | null;
    status: ReferralStatus;
    drafted_at: string;
    sent_at: string | null;
    response_at: string | null;
    follow_up_count: number;
    next_follow_up_at: string | null;
    notes: string | null;
}

// Email
export type EmailType = 'sent' | 'received';
export type EmailStatus =
    | 'draft'
    | 'queued'
    | 'sent'
    | 'delivered'
    | 'opened'
    | 'replied'
    | 'bounced'
    | 'failed';

export interface Email {
    id: number;
    user_id: number;
    thread_id: string | null;
    email_type: EmailType;
    category: string;
    from_address: string;
    to_addresses: string[];
    cc_addresses: string[];
    subject: string;
    body_text: string | null;
    body_html: string | null;
    attachments: any[];
    status: EmailStatus;
    sentiment: string | null;
    intent: string | null;
    ai_summary: string | null;
    action_required: boolean;
    suggested_action: string | null;
    sent_at: string | null;
    received_at: string | null;
    created_at: string;
}

export interface EmailStats {
    total_sent: number;
    total_received: number;
    pending_replies: number;
    action_required: number;
    by_category: Record<string, number>;
}
