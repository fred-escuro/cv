-- Seed data for system_generic_settings table
-- This script populates the table with initial values for all categories

-- Gender options
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('gender', 'male', 'Male', NULL, 1, true, NOW(), NOW()),
('gender', 'female', 'Female', NULL, 2, true, NOW(), NOW()),
('gender', 'other', 'Other', NULL, 3, true, NOW(), NOW()),
('gender', 'prefer_not_to_say', 'Prefer not to say', NULL, 4, true, NOW(), NOW());

-- Civil status options
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('civil_status', 'single', 'Single', NULL, 1, true, NOW(), NOW()),
('civil_status', 'married', 'Married', NULL, 2, true, NOW(), NOW()),
('civil_status', 'divorced', 'Divorced', NULL, 3, true, NOW(), NOW()),
('civil_status', 'widowed', 'Widowed', NULL, 4, true, NOW(), NOW()),
('civil_status', 'separated', 'Separated', NULL, 5, true, NOW(), NOW()),
('civil_status', 'civil_partnership', 'Civil Partnership', NULL, 6, true, NOW(), NOW());

-- Email types
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('email_types', 'personal', 'Personal Email', NULL, 1, true, NOW(), NOW()),
('email_types', 'work', 'Work Email', NULL, 2, true, NOW(), NOW()),
('email_types', 'other', 'Other Email', NULL, 3, true, NOW(), NOW()),
('email_types', 'academic', 'Academic Email', NULL, 4, true, NOW(), NOW());

-- Phone types
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('phone_types', 'mobile', 'Mobile', NULL, 1, true, NOW(), NOW()),
('phone_types', 'home', 'Home', NULL, 2, true, NOW(), NOW()),
('phone_types', 'work', 'Work', NULL, 3, true, NOW(), NOW()),
('phone_types', 'emergency', 'Emergency', NULL, 4, true, NOW()),
('phone_types', 'other', 'Other', NULL, 5, true, NOW(), NOW());

-- Skill categories
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('skill_categories', 'technical', 'Technical Skills', NULL, 1, true, NOW(), NOW()),
('skill_categories', 'soft', 'Soft Skills', NULL, 2, true, NOW(), NOW()),
('skill_categories', 'language', 'Languages', NULL, 3, true, NOW(), NOW()),
('skill_categories', 'framework', 'Frameworks & Libraries', NULL, 4, true, NOW(), NOW()),
('skill_categories', 'database', 'Databases', NULL, 5, true, NOW(), NOW()),
('skill_categories', 'tool', 'Development Tools', NULL, 6, true, NOW(), NOW()),
('skill_categories', 'methodology', 'Methodologies', NULL, 7, true, NOW(), NOW()),
('skill_categories', 'certification', 'Certifications', NULL, 8, true, NOW(), NOW());

-- Proficiency levels
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('proficiency_levels', 'beginner', 'Beginner', '1', 1, true, NOW(), NOW()),
('proficiency_levels', 'intermediate', 'Intermediate', '2', 2, true, NOW(), NOW()),
('proficiency_levels', 'advanced', 'Advanced', '3', 3, true, NOW(), NOW()),
('proficiency_levels', 'expert', 'Expert', '4', 4, true, NOW(), NOW()),
('proficiency_levels', 'master', 'Master', '5', 5, true, NOW(), NOW());

-- Social media platforms
INSERT INTO system_generic_settings (category, setting_key, label, value, sort_order, is_active, created_at, updated_at) VALUES
('social_platforms', 'linkedin', 'LinkedIn', NULL, 1, true, NOW(), NOW()),
('social_platforms', 'github', 'GitHub', NULL, 2, true, NOW(), NOW()),
('social_platforms', 'twitter', 'Twitter/X', NULL, 3, true, NOW(), NOW()),
('social_platforms', 'facebook', 'Facebook', NULL, 4, true, NOW(), NOW()),
('social_platforms', 'instagram', 'Instagram', NULL, 5, true, NOW(), NOW()),
('social_platforms', 'youtube', 'YouTube', NULL, 6, true, NOW(), NOW()),
('social_platforms', 'portfolio', 'Portfolio Website', NULL, 7, true, NOW(), NOW()),
('social_platforms', 'blog', 'Blog', NULL, 8, true, NOW(), NOW()),
('social_platforms', 'other', 'Other', NULL, 9, true, NOW(), NOW());
