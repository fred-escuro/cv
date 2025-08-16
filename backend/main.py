from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import json
from typing import Optional
import aiofiles
from pathlib import Path

from services.document_processor import DocumentProcessor
from services.file_converter import FileConverter
from services.text_extractor import TextExtractor
from services.ai_processor import AIProcessor
from services.json_to_pdf_converter import JSONToPDFConverter
from services.prisma_database_service import PrismaDatabaseService
from services.workflow_service import WorkflowService
from services.advanced_search_service import AdvancedSearchService
import traceback

app = FastAPI(title="CV Transform API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload and temp directories
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp")
UPLOAD_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Initialize services
document_processor = DocumentProcessor()
file_converter = FileConverter()
text_extractor = TextExtractor()
database_service = PrismaDatabaseService()
workflow_service = WorkflowService()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await database_service.initialize()
        await workflow_service.initialize()
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        # Continue without database if it's not available

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    try:
        await workflow_service.close()
        await database_service.close()
    except Exception as e:
        print(f"❌ Error closing database: {e}")

@app.get("/")
async def root():
    return {"message": "CV Transform API is running"}

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV document and process it
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.rtf', '.txt', '.json', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        # Sanitize the original filename to avoid issues with special characters
        safe_filename = file.filename.replace('\\', '_').replace('/', '_').replace(':', '_')
        original_filename = f"{file_id}_{safe_filename}"
        original_path = UPLOAD_DIR / original_filename
        
        # Save uploaded file
        async with aiofiles.open(original_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"File saved: {original_path}")
        
        # Check if file already exists in database (duplicate detection)
        try:
            print(f"🔍 Checking for duplicate file: {original_filename}")
            print(f"📁 File path: {original_path}")
            print(f"📏 File size: {original_path.stat().st_size} bytes")
            
            existing_file = await database_service.check_file_exists(original_path)
            
            if existing_file:
                print(f"📋 Duplicate file detected!")
                print(f"   - Existing file ID: {existing_file['fileId']}")
                print(f"   - Existing filename: {existing_file['originalFilename']}")
                print(f"   - File hash: {existing_file['fileHash']}")
                
                # Clean up the uploaded file since we already have it
                if original_path.exists():
                    original_path.unlink()
                
                # Return duplicate information for frontend to handle
                duplicate_response = {
                    "success": True,
                    "file_id": existing_file['fileId'],
                    "original_filename": existing_file['originalFilename'],
                    "file_type": existing_file['fileType'],
                    "is_duplicate": True,
                    "message": "File already exists in database",
                    "duplicate_file_id": existing_file['fileId'],
                    "duplicate_filename": existing_file['originalFilename']
                }
                
                print(f"📤 Returning duplicate response: {duplicate_response}")
                return duplicate_response
            else:
                print(f"✅ No duplicate found, proceeding with upload")
        except Exception as db_error:
            print(f"⚠️ Database check failed: {db_error}")
            # Continue processing even if database is not available
        
        # Start the automated workflow
        print(f"🚀 Starting automated CV workflow for: {original_filename}")
        
        # Run workflow in background (non-blocking)
        workflow_result = await workflow_service.process_cv_workflow(
            original_path, 
            file.filename, 
            file_extension
        )
        
        if workflow_result["success"]:
            return {
                "success": True,
                "file_id": workflow_result["file_id"],
                "message": workflow_result["message"],
                "processing_status": "completed",
                "workflow_completed": True,
                "text_content": workflow_result.get("text_content", ""),  # Include extracted text
                "converted_pdf_path": workflow_result.get("converted_pdf_path", ""),
                "ai_pdf_path": workflow_result.get("ai_pdf_path", ""),
                "ai_output": workflow_result.get("ai_output", {}),  # Include AI output with model info
                "ai_model": workflow_result.get("ai_output", {}).get("model_used", "OpenRouter AI") if isinstance(workflow_result.get("ai_output"), dict) else "OpenRouter AI"
            }
        else:
            # Workflow failed, but file is uploaded and ready for retry
            return {
                "success": False,
                "file_id": workflow_result["file_id"],
                "message": workflow_result["message"],
                "processing_status": "error",
                "error": workflow_result["error"],
                "can_retry": True
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in upload_cv: {e}")
        # Clean up the uploaded file if it exists
        if 'original_path' in locals() and original_path.exists():
            original_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/download-pdf/{file_id}")
async def download_pdf(file_id: str):
    """
    Download the converted PDF file
    """
    try:
        # Look for PDF files that start with the file_id and end with .pdf
        # The file converter creates files like: {file_id}_{original_filename}.pdf
        pdf_files = list(UPLOAD_DIR.glob(f"{file_id}*.pdf"))
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        pdf_path = pdf_files[0]  # Take the first matching file
        
        return FileResponse(
            path=pdf_path,
            filename=f"{file_id}_converted.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/view-pdf/{file_id}")
async def view_pdf(file_id: str, type: str = "original"):
    """
    View the converted PDF file in browser (for iframe display)
    """
    try:
        print(f"🔍 Looking for original converted PDF with file_id: {file_id}")
        print(f"🔍 Upload directory: {UPLOAD_DIR}")
        
        # Debug: List all files in uploads directory
        all_files = list(UPLOAD_DIR.glob("*"))
        print(f"🔍 All files in uploads directory: {[f.name for f in all_files]}")
        
        if type == "ai":
            # Look for AI-generated PDF
            ai_pdf_path = UPLOAD_DIR / f"{file_id}_ai_generated.pdf"
            if ai_pdf_path.exists():
                pdf_path = ai_pdf_path
                print(f"🔍 Serving AI-generated PDF: {pdf_path}")
            else:
                print(f"❌ AI-generated PDF not found for file_id: {file_id}")
                raise HTTPException(status_code=404, detail="AI-generated PDF not found")
        else:
            # Look for the original converted PDF file (not the AI-generated one)
            # The file converter creates files like: {file_id}_{original_filename}.pdf
            # We want to exclude: {file_id}_ai_generated.pdf
            pdf_files = []
            for pdf_file in UPLOAD_DIR.glob(f"{file_id}*.pdf"):
                # Exclude AI-generated PDFs
                if not pdf_file.name.endswith("_ai_generated.pdf"):
                    pdf_files.append(pdf_file)
            
            print(f"🔍 Original PDF files found (excluding AI-generated): {pdf_files}")
            print(f"🔍 Count: {len(pdf_files)}")
            
            if not pdf_files:
                print(f"❌ No original PDF files found for file_id: {file_id}")
                raise HTTPException(status_code=404, detail="Original PDF file not found")
            
            pdf_path = pdf_files[0]  # Take the first matching original PDF file
        print(f"🔍 Selected original PDF path: {pdf_path}")
        print(f"🔍 Path exists: {pdf_path.exists()}")
        print(f"🔍 Path is file: {pdf_path.is_file()}")
        print(f"🔍 File size: {pdf_path.stat().st_size if pdf_path.exists() else 'N/A'}")
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        print(f"❌ Error in view-pdf endpoint: {e}")
        print(f"❌ Exception type: {type(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{file_id}")
async def get_document_info(file_id: str):
    """
    Get document information and text content
    """
    try:
        text_path = UPLOAD_DIR / f"{file_id}_text.txt"
        
        # Look for the original converted PDF file (not the AI-generated one)
        # The file converter creates files like: {file_id}_{original_filename}.pdf
        # We want to exclude: {file_id}_ai_generated.pdf
        pdf_files = []
        for pdf_file in UPLOAD_DIR.glob(f"{file_id}*.pdf"):
            # Exclude AI-generated PDFs
            if not pdf_file.name.endswith("_ai_generated.pdf"):
                pdf_files.append(pdf_file)
        
        pdf_exists = len(pdf_files) > 0
        
        if not text_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Read text content
        async with aiofiles.open(text_path, 'r', encoding='utf-8') as f:
            text_content = await f.read()
        
        return {
            "file_id": file_id,
            "text_content": text_content,
            "pdf_exists": pdf_exists,
            "text_length": len(text_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/document/{file_id}")
async def delete_document(file_id: str):
    """
    Delete uploaded document and its processed files
    """
    try:
        # Find all files with this file_id
        files_to_delete = []
        
        # Comprehensive file cleanup - look for all file types
        file_patterns = [
            f"{file_id}_text.txt",           # Extracted text
            f"{file_id}_ai_output.json",     # AI processing output
            f"{file_id}_ai_generated.pdf",   # AI-generated PDF
            f"{file_id}_profile.pdf",        # Profile PDF
            f"{file_id}_converted.pdf",      # Converted PDF
            f"{file_id}*.pdf",               # Any PDF files with this file_id
            f"{file_id}*.txt",               # Any text files with this file_id
            f"{file_id}*.json",              # Any JSON files with this file_id
            f"{file_id}*.docx",              # Any DOCX files with this file_id
            f"{file_id}*.doc",               # Any DOC files with this file_id
            f"{file_id}_*",                  # Files with file_id prefix and original filename
            f"{file_id}*",                   # Any other files with this file_id
        ]
        
        # Add files matching each pattern
        for pattern in file_patterns:
            matching_files = list(UPLOAD_DIR.glob(pattern))
            files_to_delete.extend(matching_files)
        
        # Remove duplicates and filter out non-existent files
        files_to_delete = list(set(files_to_delete))
        existing_files = [f for f in files_to_delete if f.exists()]
        
        # Log what we're deleting
        print(f"🗑️ Deleting files for file_id {file_id}:")
        for file_path in existing_files:
            file_type = "AI-generated PDF" if file_path.name.endswith("_ai_generated.pdf") else "Original/Converted file"
            print(f"   - {file_path.name} ({file_type})")
        
        # Delete files
        for file_path in existing_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Deleted file: {file_path.name}")
            except Exception as delete_error:
                print(f"⚠️ Warning: Could not delete {file_path.name}: {delete_error}")
        
        return {"success": True, "message": f"Deleted {len(files_to_delete)} files"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-json/{file_id}")
async def process_json(file_id: str, request_data: dict):
    """
    Process a document to extract structured JSON using OpenRouter AI
    """
    try:
        # Initialize AI processor
        ai_processor = AIProcessor()
        
        # Get the extracted text content
        text_path = UPLOAD_DIR / f"{file_id}_text.txt"
        if not text_path.exists():
            raise HTTPException(status_code=404, detail="Text content not found")
        
        # Read text content
        async with aiofiles.open(text_path, 'r', encoding='utf-8') as f:
            text_content = await f.read()
        
        print(f"📊 Processing JSON for file: {file_id}")
        print(f"📏 Text content length: {len(text_content)} characters")
        
        # Check if this is a long document
        if len(text_content) > 50000:
            print(f"📋 Long document detected ({len(text_content)} chars), will use chunked processing")
        
        # Process with AI
        import time
        start_time = time.time()
        
        result = await ai_processor.process_cv_to_json(
            filename=request_data.get("filename", ""),
            text_content=text_content
        )
        
        processing_duration_ms = int((time.time() - start_time) * 1000)
        
        # Validate the result before saving
        if not result:
            raise Exception("AI processing returned empty result")
        
        if not isinstance(result, dict):
            raise Exception(f"AI processing returned invalid result type: {type(result).__name__}")
        
        # Save the JSON result to a file for later use
        json_path = UPLOAD_DIR / f"{file_id}_ai_output.json"
        json_content = json.dumps(result, indent=2, ensure_ascii=False)
        
        # Ensure we have valid content
        if not json_content.strip():
            raise Exception("Generated JSON content is empty")
        
        async with aiofiles.open(json_path, 'w', encoding='utf-8') as f:
            await f.write(json_content)
        
        print(f"✅ JSON saved to file: {json_path} ({len(json_content)} characters)")
        
        # Save AI processing results to database
        try:
            ai_model_used = getattr(ai_processor, 'primary_model', 'unknown')
            await database_service.save_cv_data(
                file_id=file_id,
                cv_data=result,
                ai_model=ai_model_used,
                processing_duration_ms=processing_duration_ms
            )
            print(f"✅ CV data saved to database for file: {file_id}")
        except Exception as db_error:
            print(f"⚠️ Failed to save CV data to database: {db_error}")
            # Continue even if database save fails
        
        print(f"✅ JSON processing completed successfully for {file_id}")
        return result
        
    except Exception as e:
        print(f"Error in JSON processing: {e}")
        # Update database with error status
        try:
            await database_service.update_processing_error(file_id, str(e))
        except Exception as db_error:
            print(f"⚠️ Failed to update database with error: {db_error}")
        
        raise HTTPException(status_code=500, detail=str(e))
        error_detail = str(e)
        
        # Try to parse error details if it's JSON
        try:
            error_data = json.loads(error_detail)
            if isinstance(error_data, dict) and error_data.get("error"):
                # Return structured error information
                return {
                    "error": True,
                    "error_message": error_data.get("error_message", "Unknown error"),
                    "raw_ai_response": error_data.get("raw_ai_response"),
                    "filename": error_data.get("filename"),
                    "text_content_preview": error_data.get("text_content_preview"),
                    "can_retry": True
                }
        except:
            pass
        
        # Fallback to simple error
        raise HTTPException(status_code=500, detail=f"JSON processing failed: {error_detail}")

@app.post("/json-to-pdf/{file_id}")
async def json_to_pdf(file_id: str):
    """
    Convert AI-generated JSON to formatted PDF
    """
    try:
        # Initialize converter
        converter = JSONToPDFConverter()
        
        # Read the JSON file
        json_path = UPLOAD_DIR / f"{file_id}_ai_output.json"
        if not json_path.exists():
            raise HTTPException(status_code=404, detail="AI output JSON not found")
        
        # Read JSON content
        async with aiofiles.open(json_path, 'r', encoding='utf-8') as f:
            json_content = await f.read()
        
        # Check if file is empty
        if not json_content.strip():
            raise HTTPException(status_code=400, detail="AI output JSON file is empty")
        
        # Parse JSON
        try:
            json_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"❌ JSON content: {json_content[:200]}...")
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Validate that we have a dictionary
        if not isinstance(json_data, dict):
            raise HTTPException(status_code=400, detail=f"Expected dictionary, got {type(json_data).__name__}")
        
        # Check for required structure
        if 'personal_information' not in json_data:
            raise HTTPException(status_code=400, detail="Missing required 'personal_information' section")
        
        # Generate PDF
        pdf_path = UPLOAD_DIR / f"{file_id}_ai_generated.pdf"
        await converter.convert_json_to_pdf(json_data, pdf_path)
        
        return {
            "success": True,
            "pdf_path": str(pdf_path),
            "message": "PDF generated successfully from AI output"
        }
        
    except Exception as e:
        print(f"Error in JSON to PDF conversion: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/view-ai-pdf/{file_id}")
async def view_ai_pdf(file_id: str):
    """
    View the AI-generated PDF file in browser
    """
    try:
        # Look for AI-generated PDF files
        pdf_files = list(UPLOAD_DIR.glob(f"{file_id}_ai_generated.pdf"))
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="AI-generated PDF not found")
        
        pdf_path = pdf_files[0]
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Database API endpoints
@app.get("/cv/{file_id}")
async def get_cv(file_id: str):
    """
    Get CV data by file ID from database
    """
    try:
        cv_data = await database_service.get_cv_by_file_id(file_id)
        if not cv_data:
            raise HTTPException(status_code=404, detail="CV not found")
        
        return cv_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/cv/{file_id}")
async def update_cv(file_id: str, cv_data: dict):
    """
    Update CV data by file ID
    """
    try:
        # Check if CV exists
        existing_cv = await database_service.get_cv_by_file_id(file_id)
        if not existing_cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Update CV data
        success = await database_service.update_cv_data(file_id, cv_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update CV data")
        
        # Return updated CV data
        updated_cv = await database_service.get_cv_by_file_id(file_id)
        return {
            "success": True,
            "message": "CV data updated successfully",
            "data": updated_cv
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cv/{file_id}/conversion-info")
async def get_conversion_info(file_id: str):
    """
    Get converted PDF filename and extracted text data by file ID
    """
    try:
        cv_data = await database_service.get_cv_by_file_id(file_id)
        if not cv_data:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Extract conversion information
        conversion_info = {
            "file_id": file_id,
            "original_filename": cv_data.get("originalFilename"),
            "converted_pdf_filename": cv_data.get("convertedPdfFilename"),
            "extracted_text_data": cv_data.get("extractedTextData"),
            "file_type": cv_data.get("fileType"),
            "processing_status": cv_data.get("processingStatus"),
            "current_step": cv_data.get("currentStep"),
            "progress_percent": cv_data.get("progressPercent"),
            "date_created": cv_data.get("dateCreated"),
            "updated_at": cv_data.get("updatedAt")
        }
        
        return conversion_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cv/{file_id}/progress")
async def get_cv_progress(file_id: str):
    """
    Get real-time progress updates for CV processing
    """
    try:
        # Get progress from database
        progress_info = await database_service.get_processing_progress(file_id)
        
        if not progress_info:
            # Check if this is a completed file that might not have progress tracking
            try:
                cv_file = await database_service.get_cv_by_file_id(file_id)
                if cv_file:
                    # File exists but no progress info, assume it's completed
                    return {
                        "success": True,
                        "file_id": file_id,
                        "status": "completed",
                        "current_step": "Processing completed",
                        "progress": 100,
                        "error": None,
                        "ai_model": "OpenRouter AI",  # Default model
                        "processing_duration_ms": 0
                    }
            except Exception:
                pass
            
            raise HTTPException(status_code=404, detail="CV processing not found")
        
        return {
            "success": True,
            "file_id": file_id,
            "status": progress_info.get("status", "unknown"),
            "current_step": progress_info.get("current_step", "Unknown"),
            "progress": progress_info.get("progress", 0),
            "error": progress_info.get("error"),
            "ai_model": progress_info.get("ai_model"),
            "processing_duration_ms": progress_info.get("processing_duration_ms")
        }
    except Exception as e:
        print(f"❌ Error getting CV progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@app.post("/cv/{file_id}/retry")
async def retry_ai_processing(file_id: str):
    """
    Retry AI processing for a specific file
    """
    try:
        # Check if file exists and can be retried
        cv_data = await database_service.get_cv_by_file_id(file_id)
        if not cv_data:
            raise HTTPException(status_code=404, detail="CV not found")
        
        if cv_data.get("processingStatus") != "error":
            raise HTTPException(status_code=400, detail="File is not in error state and cannot be retried")
        
        # Execute retry workflow
        retry_result = await workflow_service.retry_ai_processing(file_id)
        
        if retry_result["success"]:
            return {
                "success": True,
                "file_id": file_id,
                "message": retry_result["message"],
                "processing_status": "completed"
            }
        else:
            return {
                "success": False,
                "file_id": file_id,
                "error": retry_result["error"],
                "processing_status": "error"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cv/{file_id}/stop")
async def stop_ai_processing(file_id: str):
    """
    Stop AI processing for a specific file
    """
    try:
        # Validate file_id format (should be a UUID)
        try:
            import uuid
            uuid.UUID(file_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid file ID format: {file_id}")
        
        # Check if file exists and is currently processing
        cv_data = await database_service.get_cv_by_file_id(file_id)
        if not cv_data:
            raise HTTPException(status_code=404, detail="CV not found")
        
        if cv_data.get("processingStatus") != "processing":
            raise HTTPException(status_code=400, detail="File is not currently processing and cannot be stopped")
        
        # Update the processing status to stopped
        await database_service.update_processing_step(file_id, "stopped", "Processing stopped by user", 0)
        
        return {
            "success": True,
            "file_id": file_id,
            "message": "Processing stopped successfully",
            "processing_status": "stopped"
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cvs")
async def get_all_cvs(limit: int = 100, offset: int = 0):
    """
    Get all CVs with pagination
    """
    try:
        cvs = await database_service.get_all_cvs(limit=limit, offset=offset)
        return {
            "cvs": cvs,
            "limit": limit,
            "offset": offset,
            "count": len(cvs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cv/{file_id}")
async def delete_cv_file(file_id: str):
    """
    Delete a CV file and its associated data
    """
    try:
        # Validate file_id format (should be a UUID)
        try:
            import uuid
            uuid.UUID(file_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid file ID format: {file_id}")
        
        print(f"🗑️ Attempting to delete CV file: {file_id}")
        
        # Delete from database
        success = await database_service.delete_cv(file_id)
        if not success:
            raise HTTPException(status_code=404, detail="CV file not found")
        
        # Delete associated files from uploads directory
        files_to_delete = []
        
        # Comprehensive file cleanup - look for all file types created during CV processing
        file_patterns = [
            f"{file_id}_text.txt",           # Extracted text
            f"{file_id}_ai_output.json",     # AI processing output
            f"{file_id}_ai_generated.pdf",   # AI-generated PDF
            f"{file_id}_profile.pdf",        # Profile PDF
            f"{file_id}_converted.pdf",      # Converted PDF
            f"{file_id}*.pdf",               # Any PDF files with this file_id
            f"{file_id}*.txt",               # Any text files with this file_id
            f"{file_id}*.json",              # Any JSON files with this file_id
            f"{file_id}*.docx",              # Any DOCX files with this file_id
            f"{file_id}*.doc",               # Any DOC files with this file_id
            f"{file_id}*",                   # Any other files with this file_id
        ]
        
        # Add files matching each pattern
        for pattern in file_patterns:
            matching_files = list(UPLOAD_DIR.glob(pattern))
            files_to_delete.extend(matching_files)
        
        # Remove duplicates and filter out non-existent files
        files_to_delete = list(set(files_to_delete))
        existing_files = [f for f in files_to_delete if f.exists()]
        
        # Log what we're deleting
        print(f"🗑️ Deleting files for file_id {file_id}:")
        for file_path in existing_files:
            file_type = "AI-generated PDF" if file_path.name.endswith("_ai_generated.pdf") else "Original/Converted file"
            print(f"   - {file_path.name} ({file_type})")
        
        # Delete files
        for file_path in existing_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Deleted file: {file_path.name}")
            except Exception as delete_error:
                print(f"⚠️ Warning: Could not delete {file_path.name}: {delete_error}")
        
        print(f"✅ Successfully deleted CV file and {len(files_to_delete)} associated files")
        return {"success": True, "message": f"Deleted CV file and {len(files_to_delete)} associated files"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting CV file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete CV file: {str(e)}")

@app.post("/cv/reprocess")
async def reprocess_cv(file: UploadFile = File(...)):
    """
    Reprocess a CV file by uploading it and triggering a new workflow.
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.rtf', '.txt', '.json', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        # Sanitize the original filename to avoid issues with special characters
        safe_filename = file.filename.replace('\\', '_').replace('/', '_').replace(':', '_')
        original_filename = f"{file_id}_{safe_filename}"
        original_path = UPLOAD_DIR / original_filename
        
        # Save uploaded file
        async with aiofiles.open(original_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"File saved for reprocessing: {original_path}")
        
        # Start the automated workflow
        print(f"🚀 Starting automated CV workflow for reprocessed file: {original_filename}")
        
        # Run workflow in background (non-blocking)
        workflow_result = await workflow_service.process_cv_workflow(
            original_path, 
            file.filename, 
            file_extension
        )
        
        if workflow_result["success"]:
            return {
                "success": True,
                "file_id": workflow_result["file_id"],
                "message": workflow_result["message"],
                "processing_status": "completed",
                "workflow_completed": True,
                "text_content": workflow_result.get("text_content", ""),  # Include extracted text
                "converted_pdf_path": workflow_result.get("converted_pdf_path", ""),
                "ai_pdf_path": workflow_result.get("ai_pdf_path", ""),
                "ai_output": workflow_result.get("ai_output", {}),  # Include AI output with model info
                "ai_model": workflow_result.get("ai_output", {}).get("model_used", "OpenRouter AI") if isinstance(workflow_result.get("ai_output"), dict) else "OpenRouter AI"
            }
        else:
            # Workflow failed, but file is uploaded and ready for retry
            return {
                "success": False,
                "file_id": workflow_result["file_id"],
                "message": workflow_result["message"],
                "processing_status": "error",
                "error": workflow_result["error"],
                "can_retry": True
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in reprocess_cv: {e}")
        # Clean up the uploaded file if it exists
        if 'original_path' in locals() and original_path.exists():
            original_path.unlink()
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")

@app.get("/stats")
async def get_processing_stats():
    """
    Get processing statistics
    """
    try:
        stats = await database_service.get_processing_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/status")
async def get_database_status():
    """
    Get database status and table information
    """
    try:
        table_status = await database_service.verify_tables_exist()
        table_structure = await database_service.get_table_structure()
        stats = await database_service.get_processing_stats()
        
        return {
            "database_status": "connected",
            "tables": table_status,
            "structure": table_structure,
            "statistics": stats
        }
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e),
            "tables": {},
            "structure": {},
            "statistics": {}
        }

@app.get("/search/candidates")
async def search_candidates(
    name: str = None,
    skills: str = None,
    job_title: str = None,
    company: str = None,
    location: str = None,
    education_degree: str = None,
    min_experience_years: int = None,
    certifications: str = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Search candidates using normalized tables
    """
    try:
        # Parse comma-separated strings to lists
        skills_list = [s.strip() for s in skills.split(',')] if skills else None
        certifications_list = [c.strip() for c in certifications.split(',')] if certifications else None
        
        candidates = await database_service.search_candidates(
            name=name,
            skills=skills_list,
            job_title=job_title,
            company=company,
            location=location,
            education_degree=education_degree,
            min_experience_years=min_experience_years,
            certifications=certifications_list,
            limit=limit,
            offset=offset
        )
        
        return {
            "candidates": candidates,
            "total": len(candidates),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candidate/{file_id}/details")
async def get_candidate_details(file_id: str):
    """
    Get detailed candidate information from normalized tables
    """
    try:
        details = await database_service.get_candidate_details(file_id)
        if not details['file_info']:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/skills-statistics")
async def get_skills_statistics():
    """
    Get statistics about skills across all candidates
    """
    try:
        stats = await database_service.get_skills_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CV List API endpoints
@app.get("/cv-list")
async def get_cv_list(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    search_type: str = "both",  # "fulltext", "fielded", or "both"
    status_filter: str = None,
    file_type_filter: str = None
):
    """
    Get paginated list of CVs with search and filtering capabilities
    """
    try:
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build where conditions for filtering
        where_conditions = {}
        
        # Add search conditions
        if search:
            search_conditions = []
            
            # Full-text search in cv_text_lines
            if search_type in ["fulltext", "both"]:
                full_text_cv_ids = []
                try:
                    full_text_results = await database_service.search_cv_text(search, 1000)  # Get more results
                    full_text_cv_ids = list(set([result['file_id'] for result in full_text_results]))
                    print(f"🔍 Full-text search found {len(full_text_cv_ids)} CVs containing: {search}")
                    
                    if full_text_cv_ids:
                        search_conditions.append({"fileId": {"in": full_text_cv_ids}})
                        
                except Exception as e:
                    print(f"⚠️ Full-text search failed: {e}")
            
            # Fielded search in normalized tables
            if search_type in ["fielded", "both"]:
                fielded_conditions = [
                    {"originalFilename": {"contains": search, "mode": "insensitive"}},
                    {"personalInfo": {"firstName": {"contains": search, "mode": "insensitive"}}},
                    {"personalInfo": {"lastName": {"contains": search, "mode": "insensitive"}}},
                    {"personalInfo": {"emails": {"some": {"email": {"contains": search, "mode": "insensitive"}}}}},
                    {"extractedTextData": {"contains": search, "mode": "insensitive"}}
                ]
                search_conditions.extend(fielded_conditions)
            
            # Combine search conditions
            if search_conditions:
                where_conditions["OR"] = search_conditions
        
        # Add status filter
        if status_filter and status_filter != "all":
            where_conditions["processingStatus"] = status_filter
        
        # Add file type filter
        if file_type_filter and file_type_filter != "all":
            where_conditions["fileType"] = file_type_filter
        
        # Get total count for pagination
        total_count = await database_service.prisma.cvfile.count(where=where_conditions)
        
        # Get CVs with pagination and includes
        cv_files = await database_service.prisma.cvfile.find_many(
            where=where_conditions,
            take=limit,
            skip=offset,
            include={
                "personalInfo": {
                    "include": {
                        "emails": True,
                        "phones": True,
                        "socialUrls": True
                    }
                },
                "workExperience": True,
                "education": True,
                "skills": True
            },
            order=[{"dateCreated": "desc"}]
        )
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "cv_files": [cv_file.model_dump() for cv_file in cv_files],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev
            },
            "search_info": {
                "search_type": search_type,
                "search_query": search,
                "full_text_enabled": search_type in ["fulltext", "both"],
                "fielded_enabled": search_type in ["fielded", "both"]
            }
        }
        
    except Exception as e:
        print(f"❌ Error in CV list endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-cv/{cv_id}")
async def delete_cv(cv_id: str):
    """
    Delete a CV and all related files, records, and database entries
    """
    try:
        print(f"🗑️ Deleting CV with ID: {cv_id}")
        
        # First, get the CV file to get the file_id for file cleanup
        cv_file = await database_service.prisma.cvfile.find_unique(
            where={"id": int(cv_id)},
            include={
                "personalInfo": {
                    "include": {
                        "emails": True,
                        "phones": True,
                        "socialUrls": True
                    }
                },
                "workExperience": True,
                "education": True,
                "skills": True,
                "certifications": True,
                "projects": True,
                "awardsHonors": True,
                "volunteerExperience": True,
                "references": True,
                "itSystems": True
            }
        )
        
        if not cv_file:
            raise HTTPException(status_code=404, detail="CV not found")
        
        file_id = cv_file.fileId
        print(f"📁 Found CV file_id: {file_id}")
        print(f"📊 CV has {len(cv_file.workExperience or [])} work experiences")
        print(f"📊 CV has {len(cv_file.education or [])} education records")
        print(f"📊 CV has {len(cv_file.skills or [])} skills")
        print(f"📊 CV has {len(cv_file.certifications or [])} certifications")
        print(f"📊 CV has {len(cv_file.projects or [])} projects")
        print(f"📊 CV has {len(cv_file.awardsHonors or [])} awards/honors")
        print(f"📊 CV has {len(cv_file.volunteerExperience or [])} volunteer experiences")
        print(f"📊 CV has {len(cv_file.references or [])} references")
        print(f"📊 CV has {len(cv_file.itSystems or [])} IT systems")
        
        if cv_file.personalInfo:
            print(f"📊 CV has personal info with {len(cv_file.personalInfo.emails or [])} emails, {len(cv_file.personalInfo.phones or [])} phones, {len(cv_file.personalInfo.socialUrls or [])} social URLs")
        
        # Use a transaction to ensure data consistency
        async with database_service.prisma.tx() as transaction:
            # Delete all related database records first
            # Delete emails, phones, social URLs if personalInfo exists
            if cv_file.personalInfo:
                personal_info_id = cv_file.personalInfo.id
                print(f"🗑️ Deleting personal info records for ID: {personal_info_id}")
                
                # Due to foreign key constraints with ON DELETE CASCADE, 
                # emails, phones, and social URLs will be automatically deleted
                # when personal_info is deleted, so we don't need to delete them manually
                
                # Delete personal info (this will cascade delete emails, phones, social URLs)
                try:
                    await transaction.personalinfo.delete(
                        where={"id": personal_info_id}
                    )
                    print("🗑️ Deleted personal info record (and cascaded emails, phones, social URLs)")
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete personal info: {e}")
            else:
                print("ℹ️ No personal info found for this CV")
            
            # Delete work experience records
            try:
                if cv_file.workExperience:
                    await transaction.workexperience.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.workExperience)} work experience records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete work experience: {e}")
            
            # Delete education records
            try:
                if cv_file.education:
                    await transaction.education.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.education)} education records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete education: {e}")
            
            # Delete skills records
            try:
                if cv_file.skills:
                    await transaction.skill.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.skills)} skills records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete skills: {e}")
            
            # Delete certifications
            try:
                if cv_file.certifications:
                    await transaction.certification.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.certifications)} certification records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete certifications: {e}")
            
            # Delete projects
            try:
                if cv_file.projects:
                    await transaction.project.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.projects)} project records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete projects: {e}")
            
            # Delete awards and honors
            try:
                if cv_file.awardsHonors:
                    await transaction.awardhonor.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.awardsHonors)} award/honor records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete awards/honors: {e}")
            
            # Delete volunteer experience
            try:
                if cv_file.volunteerExperience:
                    await transaction.volunteerexperience.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.volunteerExperience)} volunteer experience records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete volunteer experience: {e}")
            
            # Delete references
            try:
                if cv_file.references:
                    await transaction.reference.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.references)} reference records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete references: {e}")
            
            # Delete IT systems
            try:
                if cv_file.itSystems:
                    await transaction.itsystem.delete_many(
                        where={"fileId": file_id}
                    )
                    print(f"🗑️ Deleted {len(cv_file.itSystems)} IT system records")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete IT systems: {e}")
            
            # Finally, delete the CV file record
            try:
                await transaction.cvfile.delete(
                    where={"id": int(cv_id)}
                )
                print("🗑️ Deleted CV file record")
            except Exception as e:
                print(f"❌ Error: Could not delete CV file record: {e}")
                raise Exception(f"Failed to delete CV file record: {e}")
        
        # Clean up physical files
        try:
            import os
            from pathlib import Path
            
            # Get upload directory
            upload_dir = Path("uploads")
            
            # Find and delete all files related to this CV
            files_to_delete = []
            
            # Comprehensive file cleanup - look for all file types created during CV processing
            file_patterns = [
                f"{file_id}_text.txt",           # Extracted text
                f"{file_id}_ai_output.json",     # AI processing output
                f"{file_id}_ai_generated.pdf",   # AI-generated PDF
                f"{file_id}_profile.pdf",        # Profile PDF
                f"{file_id}_converted.pdf",      # Converted PDF
                f"{file_id}*.pdf",               # Any PDF files with this file_id
                f"{file_id}*.txt",               # Any text files with this file_id
                f"{file_id}*.json",              # Any JSON files with this file_id
                f"{file_id}*.docx",              # Any DOCX files with this file_id
                f"{file_id}*.doc",               # Any DOC files with this file_id
                f"{file_id}_*",                  # Files with file_id prefix and original filename
            ]
            
            # Add files matching each pattern
            for pattern in file_patterns:
                matching_files = list(upload_dir.glob(pattern))
                files_to_delete.extend(matching_files)
                if matching_files:
                    print(f"🔍 Found {len(matching_files)} files matching pattern: {pattern}")
            
            # Look for converted PDFs by filename
            if cv_file.convertedPdfFilename:
                converted_pdf = upload_dir / cv_file.convertedPdfFilename
                if converted_pdf.exists():
                    files_to_delete.append(converted_pdf)
                    print(f"🔍 Found converted PDF: {cv_file.convertedPdfFilename}")
            
            # Remove duplicates and filter out non-existent files
            files_to_delete = list(set(files_to_delete))
            existing_files = [f for f in files_to_delete if f.exists()]
            
            print(f"🗑️ Found {len(existing_files)} files to delete")
            
            # Delete all found files
            for file_path in existing_files:
                try:
                    file_path.unlink()
                    print(f"🗑️ Deleted file: {file_path.name}")
                except Exception as delete_error:
                    print(f"⚠️ Warning: Could not delete {file_path.name}: {delete_error}")
            
        except Exception as file_error:
            print(f"⚠️ Warning: Could not delete some physical files: {file_error}")
            # Continue with deletion even if file cleanup fails
        
        print(f"✅ CV deletion completed successfully for ID: {cv_id}")
        return {"message": "CV deleted successfully", "deleted_id": cv_id}
        
    except Exception as e:
        print(f"❌ Error deleting CV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete CV: {str(e)}")

@app.get("/cv-list/filters")
async def get_cv_list_filters():
    """
    Get available filter options for CV list
    """
    try:
        # Get all CVs and extract unique values
        all_cvs = await database_service.prisma.cvfile.find_many()
        
        # Extract unique processing statuses
        status_list = list(set([cv.processingStatus for cv in all_cvs if cv.processingStatus]))
        
        # Extract unique file types
        file_type_list = list(set([cv.fileType for cv in all_cvs if cv.fileType]))
        
        return {
            "statuses": status_list,
            "file_types": file_type_list
        }
        
    except Exception as e:
        print(f"❌ Error in CV list filters endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-profile-pdf")
async def generate_profile_pdf(request_data: dict):
    """
    Generate a PDF from HTML content (styled like the AI-generated profile data)
    """
    try:
        file_id = request_data.get('fileId')
        html_content = request_data.get('htmlContent')
        css_styles = request_data.get('cssStyles')
        original_filename = request_data.get('originalFilename', 'profile')
        
        if not file_id or not html_content:
            raise HTTPException(status_code=400, detail="Missing required data: fileId and htmlContent")
        
        # Create output filename
        output_filename = f"{file_id}_profile.pdf"
        output_path = UPLOAD_DIR / output_filename
        
        # Convert HTML to PDF using reportlab with HTML-like formatting
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
            import json
            
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles for better formatting
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Add title
            story.append(Paragraph(f"Candidate Profile - {original_filename}", title_style))
            story.append(Spacer(1, 12))
            
            # Parse the HTML content to extract structured data
            # Since we can't easily parse HTML, we'll use the profileData directly
            profile_data = request_data.get('profileData')
            
            if profile_data:
                # Personal Information
                if profile_data.get('personal_information'):
                    personal_info = profile_data['personal_information']
                    story.append(Paragraph("👤 Personal Information", section_style))
                    
                    # Create personal info table
                    personal_data = []
                    if personal_info.get('first_name'):
                        personal_data.append(['First Name:', personal_info['first_name']])
                    if personal_info.get('last_name'):
                        personal_data.append(['Last Name:', personal_info['last_name']])
                    if personal_info.get('middle_name'):
                        personal_data.append(['Middle Name:', personal_info['middle_name']])
                    if personal_info.get('birth_date'):
                        personal_data.append(['Birth Date:', personal_info['birth_date']])
                    if personal_info.get('gender'):
                        personal_data.append(['Gender:', personal_info['gender']])
                    if personal_info.get('civil_status'):
                        personal_data.append(['Civil Status:', personal_info['civil_status']])
                    
                    # Address information
                    if personal_info.get('address'):
                        address = personal_info['address']
                        if address.get('street'):
                            personal_data.append(['📍 Street:', address['street']])
                        if address.get('barangay'):
                            personal_data.append(['Barangay:', address['barangay']])
                        if address.get('city'):
                            personal_data.append(['City:', address['city']])
                        if address.get('state'):
                            personal_data.append(['State/Province:', address['state']])
                        if address.get('postal_code'):
                            personal_data.append(['Postal Code:', address['postal_code']])
                        if address.get('country'):
                            personal_data.append(['Country:', address['country']])
                    
                    # Contact information
                    if personal_info.get('emails'):
                        emails = personal_info['emails']
                        if isinstance(emails, list) and emails:
                            personal_data.append(['📧 Emails:', ', '.join(emails)])
                    
                    if personal_info.get('phones'):
                        phones = personal_info['phones']
                        if isinstance(phones, list) and phones:
                            phone_text = []
                            for phone in phones:
                                if isinstance(phone, dict):
                                    phone_text.append(f"{phone.get('type', 'Phone')}: {phone.get('number', '')}")
                                else:
                                    phone_text.append(str(phone))
                            personal_data.append(['📞 Phones:', ', '.join(phone_text)])
                    
                    if personal_data:
                        personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
                        personal_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ]))
                        story.append(personal_table)
                        story.append(Spacer(1, 12))
                
                # Professional Summary
                if profile_data.get('professional_summary'):
                    story.append(Paragraph("Professional Summary", section_style))
                    story.append(Paragraph(profile_data['professional_summary'], normal_style))
                    story.append(Spacer(1, 12))
                
                # Work Experience
                if profile_data.get('work_experience'):
                    story.append(Paragraph("💼 Work Experience", section_style))
                    for job in profile_data['work_experience']:
                        job_title = job.get('job_title', '')
                        company = job.get('company_name', '')
                        location = job.get('location', '')
                        start_date = job.get('start_date', '')
                        end_date = job.get('end_date', '')
                        
                        job_text = f"<b>{job_title}</b><br/>"
                        job_text += f"{company} - {location}<br/>"
                        job_text += f"{start_date} - {end_date}"
                        
                        story.append(Paragraph(job_text, normal_style))
                        
                        if job.get('responsibilities'):
                            for resp in job['responsibilities']:
                                story.append(Paragraph(f"• {resp}", normal_style))
                        
                        story.append(Spacer(1, 8))
                
                # Education
                if profile_data.get('education'):
                    story.append(Paragraph("🎓 Education", section_style))
                    for edu in profile_data['education']:
                        degree = edu.get('degree', '')
                        institution = edu.get('institution', '')
                        location = edu.get('location', '')
                        start_date = edu.get('start_date', '')
                        end_date = edu.get('end_date', '')
                        
                        edu_text = f"<b>{degree}</b><br/>"
                        edu_text += f"{institution} - {location}<br/>"
                        edu_text += f"{start_date} - {end_date}"
                        
                        story.append(Paragraph(edu_text, normal_style))
                        story.append(Spacer(1, 8))
                
                # Skills
                if profile_data.get('skills'):
                    skills = profile_data['skills']
                    story.append(Paragraph("⭐ Skills", section_style))
                    
                    if skills.get('technical_skills'):
                        story.append(Paragraph("Technical Skills:", normal_style))
                        tech_skills = ', '.join(skills['technical_skills'])
                        story.append(Paragraph(tech_skills, normal_style))
                        story.append(Spacer(1, 6))
                    
                    if skills.get('soft_skills'):
                        story.append(Paragraph("Soft Skills:", normal_style))
                        soft_skills = ', '.join(skills['soft_skills'])
                        story.append(Paragraph(soft_skills, normal_style))
                        story.append(Spacer(1, 6))
                    
                    if skills.get('computer_languages'):
                        story.append(Paragraph("Programming Languages:", normal_style))
                        for lang in skills['computer_languages']:
                            if isinstance(lang, dict):
                                lang_text = f"{lang.get('language', '')} ({lang.get('proficiency', '')})"
                            else:
                                lang_text = str(lang)
                            story.append(Paragraph(f"• {lang_text}", normal_style))
                
                # Build the PDF
                doc.build(story)
                
            else:
                # Fallback: create a simple text-based PDF
                story.append(Paragraph("Profile Data", title_style))
                story.append(Paragraph("No structured data available", normal_style))
                doc.build(story)
            
        except Exception as e:
            print(f"⚠️ ReportLab PDF generation failed: {e}")
            # Final fallback to JSON converter
            try:
                from services.json_to_pdf_converter import JSONToPDFConverter
                profile_data = request_data.get('profileData')
                if profile_data:
                    json_to_pdf_converter = JSONToPDFConverter()
                    await json_to_pdf_converter.convert_json_to_pdf(profile_data, output_path)
                else:
                    raise HTTPException(status_code=500, detail="No profile data available for PDF generation")
            except Exception as fallback_error:
                print(f"❌ Final fallback also failed: {fallback_error}")
                raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(fallback_error)}")
        
        # Return the PDF file
        if output_path.exists():
            return FileResponse(
                path=str(output_path),
                filename=output_filename,
                media_type='application/pdf'
            )
        else:
            raise HTTPException(status_code=500, detail="PDF generation failed")
            
    except Exception as e:
        print(f"❌ Error generating profile PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

# CV Text Search API Endpoints

@app.get("/api/search/cv-text")
async def search_cv_text(q: str, limit: int = 50):
    """
    Search across all CV text content using full-text search
    """
    try:
        results = await database_service.search_cv_text(q, limit)
        return {"success": True, "results": results, "query": q}
    except Exception as e:
        print(f"❌ Full-text search failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/search/cv-text-partial")
async def search_cv_text_partial(term: str, limit: int = 50):
    """
    Partial text search using trigram matching
    """
    try:
        results = await database_service.search_cv_text_partial(term, limit)
        return {"success": True, "results": results, "term": term}
    except Exception as e:
        print(f"❌ Partial text search failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/search/cv-context/{file_id}/{line_number}")
async def get_cv_context(file_id: str, line_number: int, context: int = 3):
    """
    Get context around a specific text line
    """
    try:
        context_data = await database_service.get_cv_context(file_id, line_number, context)
        return {"success": True, "context": context_data}
    except Exception as e:
        print(f"❌ Failed to get CV context: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/cv/{file_id}/text-lines")
async def get_cv_text_lines(file_id: str, limit: int = 100):
    """
    Get all text lines for a specific CV file
    """
    try:
        text_lines = await database_service.get_cv_text_lines(file_id, limit)
        return {"success": True, "data": text_lines, "file_id": file_id}
    except Exception as e:
        print(f"❌ Failed to get CV text lines: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/search/cv-advanced")
async def advanced_search_cv(q: str, limit: int = 50):
    """
    Advanced search CV content with boolean operators (AND, OR) and parentheses
    """
    try:
        advanced_search = AdvancedSearchService()
        await advanced_search.initialize()
        
        try:
            debug_response = await advanced_search.advanced_search_with_debug(q, limit)
            
            return {
                "success": True,
                "results": debug_response["results"],
                "query": q,
                "query_type": "advanced",
                "debug_info": debug_response["debug"]
            }
        finally:
            await advanced_search.close()
            
    except Exception as e:
        print(f"❌ Error in advanced CV search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/cv-advanced-debug")
async def advanced_search_cv_debug(q: str, limit: int = 50):
    """
    Debug endpoint to test individual searches
    """
    try:
        # Test individual searches
        managing_results = await database_service.search_cv_text("managing", limit)
        radix_results = await database_service.search_cv_text("radix", limit)
        
        return {
            "success": True,
            "managing_search": {
                "count": len(managing_results),
                "file_ids": [r.get("file_id", "NO_FILE_ID") for r in managing_results],
                "sample_result": managing_results[0] if managing_results else None
            },
            "radix_search": {
                "count": len(radix_results),
                "file_ids": [r.get("file_id", "NO_FILE_ID") for r in radix_results],
                "sample_result": radix_results[0] if radix_results else None
            }
        }
    except Exception as e:
        print(f"❌ Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Settings API Endpoints

@app.get("/api/settings/debug")
async def debug_database_state():
    """Debug endpoint to check database state"""
    try:
        await database_service.debug_database_state()
        return {"success": True, "message": "Check console for debug output"}
    except Exception as e:
        print(f"❌ Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

@app.get("/api/settings/deleted")
async def get_deleted_settings():
    """Get all soft-deleted settings grouped by category"""
    try:
        settings = await database_service.get_deleted_settings()
        return {"success": True, "data": settings}
    except Exception as e:
        print(f"❌ Error fetching deleted settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch deleted settings: {str(e)}")

@app.get("/api/settings/{category}")
async def get_settings_by_category(category: str):
    """Get all active settings for a specific category"""
    try:
        settings = await database_service.get_settings_by_category(category)
        return {"success": True, "data": settings}
    except Exception as e:
        print(f"❌ Error fetching settings for category {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")

@app.get("/api/settings")
async def get_all_settings():
    """Get all settings grouped by category"""
    try:
        settings = await database_service.get_all_settings()
        return {"success": True, "data": settings}
    except Exception as e:
        print(f"❌ Error fetching all settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")

@app.post("/api/settings")
async def create_setting(setting_data: dict):
    """Create a new setting"""
    try:
        setting = await database_service.create_setting(setting_data)
        return {"success": True, "data": setting}
    except Exception as e:
        print(f"❌ Error creating setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create setting: {str(e)}")

@app.put("/api/settings/{id}")
async def update_setting(id: int, setting_data: dict):
    """Update an existing setting"""
    try:
        setting = await database_service.update_setting(id, setting_data)
        return {"success": True, "data": setting}
    except Exception as e:
        print(f"❌ Error updating setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update setting: {str(e)}")

@app.delete("/api/settings/{id}")
async def delete_setting(id: int):
    """Delete a setting (soft delete by setting isActive to false)"""
    try:
        result = await database_service.delete_setting(id)
        return {"success": True, "message": "Setting deleted successfully"}
    except Exception as e:
        print(f"❌ Error deleting setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete setting: {str(e)}")

@app.post("/api/settings/{id}/restore")
async def restore_setting(id: int):
    """Restore a soft-deleted setting"""
    try:
        setting = await database_service.restore_setting(id)
        return {"success": True, "data": setting, "message": "Setting restored successfully"}
    except Exception as e:
        print(f"❌ Error restoring setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore setting: {str(e)}")

@app.delete("/api/settings/{id}/permanent")
async def permanently_delete_setting(id: int):
    """Permanently delete a setting from the database"""
    try:
        result = await database_service.permanently_delete_setting(id)
        return {"success": True, "message": "Setting permanently deleted"}
    except Exception as e:
        print(f"❌ Error permanently deleting setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to permanently delete setting: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
