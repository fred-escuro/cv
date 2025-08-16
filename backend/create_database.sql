-- Create database (run this as superuser)
-- CREATE DATABASE cv;

-- Connect to the cv database and run the following:

-- Create CV files table
CREATE TABLE IF NOT EXISTS cv_files (
    id SERIAL PRIMARY KEY,
    file_id UUID UNIQUE NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT
);

-- Create CV data table
CREATE TABLE IF NOT EXISTS cv_data (
    id SERIAL PRIMARY KEY,
    file_id UUID UNIQUE NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    personal_information JSONB,
    professional_summary TEXT,
    work_experience JSONB,
    it_system_used JSONB,
    education JSONB,
    skills JSONB,
    certifications JSONB,
    projects JSONB,
    awards_and_honors JSONB,
    volunteer_experience JSONB,
    interests JSONB,
    references JSONB,
    additional_information JSONB,
    ai_processing_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_model_used VARCHAR(100),
    processing_duration_ms INTEGER
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cv_files_hash ON cv_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_cv_files_filename ON cv_files(original_filename);
CREATE INDEX IF NOT EXISTS idx_cv_data_file_id ON cv_data(file_id);
CREATE INDEX IF NOT EXISTS idx_cv_files_status ON cv_files(processing_status);

-- Create indexes for JSONB columns for better query performance
CREATE INDEX IF NOT EXISTS idx_cv_data_personal_info ON cv_data USING GIN (personal_information);
CREATE INDEX IF NOT EXISTS idx_cv_data_work_experience ON cv_data USING GIN (work_experience);
CREATE INDEX IF NOT EXISTS idx_cv_data_education ON cv_data USING GIN (education);
CREATE INDEX IF NOT EXISTS idx_cv_data_skills ON cv_data USING GIN (skills);

-- Create normalized tables for better searchability

-- Personal Information table
CREATE TABLE IF NOT EXISTS cv_personal_info (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    phone_type VARCHAR(20),
    birth_date DATE,
    gender VARCHAR(20),
    civil_status VARCHAR(50),
    street VARCHAR(255),
    barangay VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    desired_city VARCHAR(100),
    desired_state VARCHAR(100),
    desired_country VARCHAR(100),
    open_to_work_from_home BOOLEAN,
    open_to_work_onsite BOOLEAN,
    social_urls TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Work Experience table
CREATE TABLE IF NOT EXISTS cv_work_experience (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    location VARCHAR(255),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    responsibilities TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Education table
CREATE TABLE IF NOT EXISTS cv_education (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    institution VARCHAR(255),
    location VARCHAR(255),
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3,2),
    honors VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills table
CREATE TABLE IF NOT EXISTS cv_skills (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_type VARCHAR(50) NOT NULL, -- 'technical', 'soft', 'language'
    proficiency VARCHAR(50), -- for languages
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Certifications table
CREATE TABLE IF NOT EXISTS cv_certifications (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiration_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table
CREATE TABLE IF NOT EXISTS cv_projects (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    project_url VARCHAR(500),
    technologies TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Awards and Honors table
CREATE TABLE IF NOT EXISTS cv_awards_honors (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    date_received DATE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Volunteer Experience table
CREATE TABLE IF NOT EXISTS cv_volunteer_experience (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    role VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    location VARCHAR(255),
    start_date DATE,
    end_date DATE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- References table
CREATE TABLE IF NOT EXISTS cv_references (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- IT Systems Used table
CREATE TABLE IF NOT EXISTS cv_it_systems (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES cv_files(file_id) ON DELETE CASCADE,
    system_name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for normalized tables
CREATE INDEX IF NOT EXISTS idx_personal_info_file_id ON cv_personal_info(file_id);
CREATE INDEX IF NOT EXISTS idx_personal_info_name ON cv_personal_info(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_personal_info_email ON cv_personal_info(email);
CREATE INDEX IF NOT EXISTS idx_personal_info_location ON cv_personal_info(city, state, country);

CREATE INDEX IF NOT EXISTS idx_work_exp_file_id ON cv_work_experience(file_id);
CREATE INDEX IF NOT EXISTS idx_work_exp_job_title ON cv_work_experience(job_title);
CREATE INDEX IF NOT EXISTS idx_work_exp_company ON cv_work_experience(company_name);
CREATE INDEX IF NOT EXISTS idx_work_exp_dates ON cv_work_experience(start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_education_file_id ON cv_education(file_id);
CREATE INDEX IF NOT EXISTS idx_education_degree ON cv_education(degree);
CREATE INDEX IF NOT EXISTS idx_education_institution ON cv_education(institution);

CREATE INDEX IF NOT EXISTS idx_skills_file_id ON cv_skills(file_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON cv_skills(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_type ON cv_skills(skill_type);

CREATE INDEX IF NOT EXISTS idx_certifications_file_id ON cv_certifications(file_id);
CREATE INDEX IF NOT EXISTS idx_certifications_name ON cv_certifications(name);

CREATE INDEX IF NOT EXISTS idx_projects_file_id ON cv_projects(file_id);
CREATE INDEX IF NOT EXISTS idx_projects_title ON cv_projects(title);

CREATE INDEX IF NOT EXISTS idx_it_systems_file_id ON cv_it_systems(file_id);
CREATE INDEX IF NOT EXISTS idx_it_systems_name ON cv_it_systems(system_name);

-- Grant permissions to the fredmann user
GRANT ALL PRIVILEGES ON TABLE cv_files TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_data TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_personal_info TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_work_experience TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_education TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_skills TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_certifications TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_projects TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_awards_honors TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_volunteer_experience TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_references TO fredmann;
GRANT ALL PRIVILEGES ON TABLE cv_it_systems TO fredmann;

GRANT USAGE, SELECT ON SEQUENCE cv_files_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_data_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_personal_info_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_work_experience_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_education_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_skills_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_certifications_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_projects_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_awards_honors_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_volunteer_experience_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_references_id_seq TO fredmann;
GRANT USAGE, SELECT ON SEQUENCE cv_it_systems_id_seq TO fredmann;
