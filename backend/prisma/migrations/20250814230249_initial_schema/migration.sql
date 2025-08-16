-- CreateTable
CREATE TABLE "public"."cv_files" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "original_filename" VARCHAR(255) NOT NULL,
    "file_type" VARCHAR(10) NOT NULL,
    "file_size" BIGINT NOT NULL,
    "file_hash" VARCHAR(64) NOT NULL,
    "converted_pdf_filename" VARCHAR(255),
    "extracted_text_data" TEXT,
    "ai_generated_json" JSONB,
    "date_created" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "date_modified" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processing_status" VARCHAR(50) NOT NULL DEFAULT 'pending',
    "current_step" VARCHAR(100),
    "progress_percent" INTEGER NOT NULL DEFAULT 0,
    "error_message" TEXT,

    CONSTRAINT "cv_files_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_personal_info" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "first_name" VARCHAR(100),
    "middle_name" VARCHAR(100),
    "last_name" VARCHAR(100),
    "birth_date" DATE,
    "gender" VARCHAR(20),
    "civil_status" VARCHAR(50),
    "street" VARCHAR(255),
    "barangay" VARCHAR(100),
    "city" VARCHAR(100),
    "state" VARCHAR(100),
    "postal_code" VARCHAR(20),
    "country" VARCHAR(100),
    "desired_city" VARCHAR(100),
    "desired_state" VARCHAR(100),
    "desired_country" VARCHAR(100),
    "open_to_work_from_home" BOOLEAN,
    "open_to_work_onsite" BOOLEAN,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_personal_info_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_work_experience" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "job_title" VARCHAR(255) NOT NULL,
    "company_name" VARCHAR(255),
    "location" VARCHAR(255),
    "start_date" DATE,
    "end_date" DATE,
    "is_current" BOOLEAN NOT NULL DEFAULT false,
    "responsibilities" TEXT[],
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_work_experience_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_education" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "degree" VARCHAR(255) NOT NULL,
    "institution" VARCHAR(255),
    "location" VARCHAR(255),
    "start_date" DATE,
    "end_date" DATE,
    "gpa" DECIMAL(3,2),
    "honors" VARCHAR(255),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_education_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_skills" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "skill_name" VARCHAR(255) NOT NULL,
    "skill_type" VARCHAR(50) NOT NULL,
    "proficiency" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_skills_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_certifications" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "issuing_organization" VARCHAR(255),
    "issue_date" DATE,
    "expiration_date" DATE,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_certifications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_projects" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "start_date" DATE,
    "end_date" DATE,
    "project_url" VARCHAR(500),
    "technologies" TEXT[],
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_awards_honors" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "issuing_organization" VARCHAR(255),
    "date_received" DATE,
    "description" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_awards_honors_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_volunteer_experience" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "role" VARCHAR(255) NOT NULL,
    "organization" VARCHAR(255),
    "location" VARCHAR(255),
    "start_date" DATE,
    "end_date" DATE,
    "description" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_volunteer_experience_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_references" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "relationship" VARCHAR(255),
    "email" VARCHAR(255),
    "phone" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_references_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_it_systems" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "system_name" VARCHAR(255) NOT NULL,
    "abbreviation" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_it_systems_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_emails" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "email_type" VARCHAR(50),
    "is_primary" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_emails_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_phones" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "phone" VARCHAR(50) NOT NULL,
    "phone_type" VARCHAR(20),
    "is_primary" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_phones_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."cv_social_urls" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "url" VARCHAR(500) NOT NULL,
    "platform" VARCHAR(100),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_social_urls_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."system_generic_settings" (
    "id" SERIAL NOT NULL,
    "category" VARCHAR(100) NOT NULL,
    "setting_key" VARCHAR(100) NOT NULL,
    "label" VARCHAR(255) NOT NULL,
    "value" VARCHAR(255),
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "system_generic_settings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "cv_files_file_id_key" ON "public"."cv_files"("file_id");

-- CreateIndex
CREATE UNIQUE INDEX "cv_files_file_hash_key" ON "public"."cv_files"("file_hash");

-- CreateIndex
CREATE UNIQUE INDEX "cv_personal_info_file_id_key" ON "public"."cv_personal_info"("file_id");

-- CreateIndex
CREATE UNIQUE INDEX "system_generic_settings_category_setting_key_key" ON "public"."system_generic_settings"("category", "setting_key");

-- AddForeignKey
ALTER TABLE "public"."cv_personal_info" ADD CONSTRAINT "cv_personal_info_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_work_experience" ADD CONSTRAINT "cv_work_experience_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_education" ADD CONSTRAINT "cv_education_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_skills" ADD CONSTRAINT "cv_skills_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_certifications" ADD CONSTRAINT "cv_certifications_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_projects" ADD CONSTRAINT "cv_projects_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_awards_honors" ADD CONSTRAINT "cv_awards_honors_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_volunteer_experience" ADD CONSTRAINT "cv_volunteer_experience_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_references" ADD CONSTRAINT "cv_references_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_it_systems" ADD CONSTRAINT "cv_it_systems_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_emails" ADD CONSTRAINT "cv_emails_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_personal_info"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_phones" ADD CONSTRAINT "cv_phones_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_personal_info"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."cv_social_urls" ADD CONSTRAINT "cv_social_urls_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_personal_info"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;
