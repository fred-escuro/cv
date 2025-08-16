# Enhanced CV Processing Workflow

## Overview

The CV processing system now features a fully automated workflow that handles the entire process from document upload to AI-generated PDF creation, with real-time progress tracking and error handling.

## Workflow Steps

### 1. File Upload & Validation
- **Status**: `pending` → `processing`
- **Progress**: 0% → 10%
- **Step**: "File uploaded"
- **Actions**: 
  - Validate file type
  - Generate unique file ID
  - Save file to upload directory
  - Check for duplicates

### 2. PDF Conversion
- **Status**: `processing`
- **Progress**: 10% → 20%
- **Step**: "Converting to PDF"
- **Actions**:
  - Convert document to PDF format
  - Handle various input formats (DOCX, RTF, TXT, images)
  - Extract text content using OCR if needed

### 3. Text Extraction
- **Status**: `processing`
- **Progress**: 20% → 30%
- **Step**: "Extracting text content"
- **Actions**:
  - Extract text from converted PDF
  - Store extracted text in database
  - Update PDF filename in database

### 4. AI Processing
- **Status**: `processing`
- **Progress**: 30% → 50%
- **Step**: "Processing with AI"
- **Actions**:
  - Send extracted text to AI service
  - Generate structured CV data
  - Parse personal info, work experience, skills, etc.

### 5. Database Storage
- **Status**: `processing`
- **Progress**: 50% → 70%
- **Step**: "Saving AI data to database"
- **Actions**:
  - Save AI JSON to `cv_data` table
  - Populate normalized tables:
    - `cv_personal_info`
    - `cv_work_experience`
    - `cv_education`
    - `cv_skills`
    - `cv_certifications`
    - `cv_projects`
    - `cv_awards_honors`
    - `cv_volunteer_experience`
    - `cv_references`
    - `cv_it_systems`

### 6. AI PDF Generation
- **Status**: `processing`
- **Progress**: 70% → 85%
- **Step**: "Generating AI-based PDF"
- **Actions**:
  - Create formatted PDF from AI JSON data
  - Apply professional styling and layout
  - Save as `{file_id}_ai_generated.pdf`

### 7. Completion
- **Status**: `processing` → `completed`
- **Progress**: 85% → 100%
- **Step**: "Processing completed"
- **Actions**:
  - Update final status
  - Mark workflow as complete

## Error Handling & Retry

### Error States
- **Status**: `error`
- **Progress**: 0%
- **Step**: "Error occurred"
- **Actions Available**:
  - User can retry AI processing
  - File remains in database with extracted text
  - No need to re-upload document

### Retry Functionality
- **Endpoint**: `POST /cv/{file_id}/retry`
- **Actions**:
  - Reset processing status
  - Retry AI processing with existing text
  - Regenerate normalized data
  - Create new AI PDF

## API Endpoints

### Upload & Processing
- `POST /upload-cv` - Upload document and start workflow
- `GET /cv/{file_id}/progress` - Get real-time processing progress
- `POST /cv/{file_id}/retry` - Retry AI processing

### Progress Tracking
- `GET /cv/{file_id}/conversion-info` - Get conversion details
- `GET /cv/{file_id}` - Get complete CV data
- `GET /cvs` - List all CVs with status

### File Access
- `GET /download-pdf/{file_id}` - Download converted PDF
- `GET /view-pdf/{file_id}` - View PDF in browser
- `GET /ai-pdf/{file_id}` - Download AI-generated PDF

## Database Schema Updates

### New Fields in `cv_files` Table
```sql
ALTER TABLE cv_files ADD COLUMN current_step VARCHAR(100);
ALTER TABLE cv_files ADD COLUMN progress_percent INTEGER DEFAULT 0;
ALTER TABLE cv_files ADD COLUMN converted_pdf_filename VARCHAR(255);
ALTER TABLE cv_files ADD COLUMN extracted_text_data TEXT;
```

### Processing Status Values
- `pending` - Ready to start
- `processing` - Workflow in progress
- `completed` - Successfully finished
- `error` - Failed, can retry

## Progress Tracking Response

```json
{
  "file_id": "12345678-1234-1234-1234-123456789abc",
  "original_filename": "resume.docx",
  "processing_status": "processing",
  "current_step": "Processing with AI",
  "progress_percent": 50,
  "error_message": null,
  "date_created": "2024-01-15T10:30:00Z",
  "date_modified": "2024-01-15T10:35:00Z",
  "can_retry": false
}
```

## Benefits

### For Users
- **Real-time Progress**: See exactly what's happening
- **No Manual Steps**: Fully automated from upload to completion
- **Error Recovery**: Retry failed AI processing without re-uploading
- **Complete Audit Trail**: Track every step of the process

### For System
- **Consistent Processing**: Standardized workflow for all documents
- **Better Error Handling**: Graceful failure with recovery options
- **Progress Monitoring**: Track system performance and bottlenecks
- **Data Integrity**: Ensure all steps complete before marking as done

## Usage Examples

### Start Processing
```bash
curl -X POST "http://localhost:8000/upload-cv" \
  -F "file=@resume.docx"
```

### Monitor Progress
```bash
curl "http://localhost:8000/cv/{file_id}/progress"
```

### Retry on Error
```bash
curl -X POST "http://localhost:8000/cv/{file_id}/retry"
```

## Error Scenarios & Solutions

### Common Errors
1. **OCR Not Available**: Install Tesseract OCR
2. **File Format Unsupported**: Convert to supported format
3. **AI Processing Failed**: Use retry endpoint
4. **Database Connection**: Check PostgreSQL service

### Recovery Actions
- **Immediate Retry**: For transient AI failures
- **File Re-upload**: For corrupted files
- **Manual Processing**: For complex documents
- **System Restart**: For service issues

## Monitoring & Maintenance

### Progress Tracking
- Monitor processing times per step
- Identify bottlenecks in workflow
- Track success/failure rates
- Monitor AI processing performance

### Database Maintenance
- Regular cleanup of temporary files
- Monitor table sizes and performance
- Backup normalized data regularly
- Archive completed workflows

## Future Enhancements

### Planned Features
- **Batch Processing**: Handle multiple files
- **Priority Queues**: Process urgent documents first
- **Webhook Notifications**: Real-time status updates
- **Advanced Retry Logic**: Exponential backoff
- **Processing Analytics**: Detailed performance metrics

### Integration Options
- **Webhook Support**: Notify external systems
- **API Rate Limiting**: Control processing load
- **Custom AI Models**: Support multiple AI providers
- **Template System**: Customizable PDF outputs
