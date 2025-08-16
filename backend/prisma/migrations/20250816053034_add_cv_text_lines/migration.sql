/*
  Warnings:

  - You are about to drop the column `date_modified` on the `cv_files` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "cv_files" DROP COLUMN "date_modified",
ADD COLUMN     "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- CreateTable
CREATE TABLE "cv_text_lines" (
    "id" SERIAL NOT NULL,
    "file_id" UUID NOT NULL,
    "line_number" INTEGER NOT NULL,
    "line_text" TEXT NOT NULL,
    "line_type" VARCHAR(50),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "cv_text_lines_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "cv_text_lines_file_id_line_number_key" ON "cv_text_lines"("file_id", "line_number");

-- AddForeignKey
ALTER TABLE "cv_text_lines" ADD CONSTRAINT "cv_text_lines_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "cv_files"("file_id") ON DELETE CASCADE ON UPDATE CASCADE;
