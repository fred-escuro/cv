-- Enable trigram extension for better partial matching (MUST BE FIRST)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- CreateTable
CREATE TABLE "public"."cv_text_lines" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "line_number" INTEGER NOT NULL,
    "line_text" TEXT NOT NULL,
    "line_type" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_text_lines_pkey" PRIMARY KEY ("id")
);

-- Create unique constraint for file_id and line_number combination
CREATE UNIQUE INDEX "cv_text_lines_file_id_line_number_key" ON "public"."cv_text_lines"("file_id", "line_number");

-- Create full-text search index
CREATE INDEX "idx_cv_text_lines_fts" ON "public"."cv_text_lines" USING gin(to_tsvector('english', line_text));

-- Create regular text index for partial matching (AFTER pg_trgm extension is created)
CREATE INDEX "idx_cv_text_lines_text" ON "public"."cv_text_lines" USING gin(line_text gin_trgm_ops);

-- Add foreign key constraint
ALTER TABLE "public"."cv_text_lines" ADD CONSTRAINT "cv_text_lines_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;
