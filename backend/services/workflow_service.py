#!/usr/bin/env python3
"""
Workflow service to handle automated CV processing pipeline
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from services.prisma_database_service import PrismaDatabaseService
from services.document_processor import DocumentProcessor
from services.ai_processor import AIProcessor
from services.json_to_pdf_converter import JSONToPDFConverter
from services.text_line_processor import TextLineProcessor

class WorkflowService:
    """
    Service to handle the automated CV processing workflow
    """
    
    def __init__(self):
        self.database_service = PrismaDatabaseService()
        self.document_processor = DocumentProcessor()
        self.ai_processor = AIProcessor()
        self.json_converter = JSONToPDFConverter()
        self.text_line_processor = TextLineProcessor()
    
    def _convert_snake_to_camel_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert snake_case keys to camelCase keys for database compatibility
        """
        if not isinstance(data, dict):
            return data
        
        converted = {}
        for key, value in data.items():
            # Convert snake_case to camelCase
            camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
            
            # Recursively convert nested dictionaries
            if isinstance(value, dict):
                converted[camel_key] = self._convert_snake_to_camel_case(value)
            elif isinstance(value, list):
                # Convert items in lists if they are dictionaries
                converted[camel_key] = [
                    self._convert_snake_to_camel_case(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[camel_key] = value
        
        return converted
    
    async def initialize(self):
        """Initialize all services"""
        try:
            await self.database_service.initialize()
            print("✅ Database service initialized successfully")
        except Exception as db_error:
            print(f"⚠️ Database service initialization failed: {db_error}")
            print("📝 Workflow will continue without database persistence")
            # Continue without database - the workflow can still process files
    
    async def close(self):
        """Close all services"""
        await self.database_service.close()
    
    async def process_cv_workflow(self, file_path: Path, original_filename: str, file_type: str) -> Dict[str, Any]:
        """
        Execute the complete CV processing workflow
        """
        file_id = str(uuid.uuid4())
        
        try:
            print(f"🚀 Starting CV workflow for file: {original_filename}")
            
            # Step 1: Save file info and start processing
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "File uploaded", 10
                )
                file_hash = await self.database_service.save_file_info(
                    file_id, file_path, original_filename, file_type
                )
                print(f"✅ Step 1: File info saved to database (10%)")
            except Exception as db_error:
                print(f"❌ Database operations failed at step 1: {db_error}")
                print("🛑 Cannot continue workflow without proper database initialization")
                raise Exception(f"Database initialization failed: {db_error}")
            
            # Step 2: Convert to PDF
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Converting to PDF", 20
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            conversion_result = await self.document_processor.process_document(file_path, file_type)
            
            if not conversion_result.get("pdf_path"):
                raise Exception("PDF conversion failed")
            
            # Rename the converted PDF to follow the expected naming pattern
            original_pdf_path = Path(conversion_result["pdf_path"])
            if original_pdf_path.exists():
                # Create the new filename: {file_id}_{original_filename}.pdf
                new_pdf_filename = f"{file_id}_{original_filename}"
                if not new_pdf_filename.endswith('.pdf'):
                    new_pdf_filename += '.pdf'
                
                new_pdf_path = Path("uploads") / new_pdf_filename
                
                # Move/rename the PDF file
                import shutil
                shutil.move(str(original_pdf_path), str(new_pdf_path))
                
                print(f"📁 Renamed PDF from {original_pdf_path.name} to {new_pdf_path.name}")
                
                # Update the conversion result with the new path
                conversion_result["pdf_path"] = str(new_pdf_path)
            else:
                print(f"⚠️ Warning: Original PDF not found at {original_pdf_path}")
            
            print(f"✅ Step 2: PDF conversion completed (20%)")
            
            # Step 3: Extract text content
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Extracting text content", 30
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            extracted_text = conversion_result.get("text_content", "")
            if not extracted_text or extracted_text.strip() == "":
                raise Exception("Text extraction failed - no content extracted")
            
            # Update database with PDF conversion info
            try:
                pdf_filename = Path(conversion_result["pdf_path"]).name
                await self.database_service.update_converted_pdf_info(
                    file_id, pdf_filename, extracted_text
                )
                print(f"✅ Step 3: Text extraction completed and saved to database (30%)")
            except Exception as db_error:
                print(f"❌ Database save failed at step 3: {db_error}")
                print("🛑 Cannot continue workflow without proper database updates")
                raise Exception(f"Database update failed: {db_error}")
            
            # Step 4: Process text into searchable lines and save to database
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Processing text lines for search", 35
                )
                
                # Process text into searchable lines
                text_lines = await self.text_line_processor.process_text_to_lines(
                    extracted_text, 
                    file_id
                )
                
                # Save text lines to database
                await self.database_service.save_text_lines(file_id, text_lines)
                
                print(f"✅ Step 4: Text lines processed and saved ({len(text_lines)} lines)")
                
            except Exception as text_error:
                print(f"⚠️ Text line processing failed: {text_error}")
                # Continue with workflow - this is not critical
            
            # Step 5: Send to AI for processing
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Processing with AI", 50
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            ai_result_info = await self.ai_processor.process_cv_to_json(original_filename, extracted_text)
            
            # Extract the actual AI result and model information
            ai_result = ai_result_info.get("ai_data") if isinstance(ai_result_info, dict) else ai_result_info
            ai_model = ai_result_info.get("model_used", "OpenRouter AI") if isinstance(ai_result_info, dict) else "OpenRouter AI"
            processing_duration_ms = ai_result_info.get("processing_duration_ms", 0) if isinstance(ai_result_info, dict) else 0
            
            # The AI processor returns the CV data directly, not wrapped in a cv_data key
            if not ai_result:
                raise Exception("AI processing failed - no response returned")
            
            # Validate that we have the required personal information
            if not isinstance(ai_result, dict) or "personal_information" not in ai_result:
                raise Exception("AI processing failed - invalid response structure")
            
            print(f"✅ Step 4: AI processing completed with model {ai_model} (50%)")
            
            # Step 6: Save AI JSON to database
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Saving AI data to database", 70
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            try:
                # Convert snake_case keys to camelCase for database compatibility
                converted_cv_data = self._convert_snake_to_camel_case(ai_result)
                
                # Add AI model information to the original response
                ai_result_with_metadata = {
                    **ai_result,
                    "ai_model": ai_model,
                    "processing_duration_ms": processing_duration_ms,
                    "model_used": ai_model
                }
                
                await self.database_service.save_cv_data(
                    file_id, 
                    converted_cv_data,  # Use converted data with camelCase keys for normalized tables
                    ai_model=ai_model,  # Use the actual model that was used
                    processing_duration_ms=processing_duration_ms,  # Use the actual processing duration
                    original_ai_response=ai_result_with_metadata  # Pass AI response with metadata for ai_generated_json
                )
                print(f"✅ Step 5: AI data saved to database with model {ai_model} (70%)")
            except Exception as db_error:
                print(f"⚠️ Database save failed, but continuing workflow: {db_error}")
                print(f"📊 CV data available in memory: {list(ai_result.keys())}")
                # Continue with the workflow even if database save fails
            
            # Step 7: Create PDF based on AI JSON
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Generating AI-based PDF", 85
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            # Create output path for AI PDF
            ai_pdf_path = Path("uploads") / f"{file_id}_ai_generated.pdf"
            
            ai_pdf_path = await self.json_converter.convert_json_to_pdf(
                ai_result,  # Use ai_result directly since it contains the CV data
                ai_pdf_path
            )
            
            if not ai_pdf_path:
                raise Exception("AI PDF generation failed")
            
            print(f"✅ Step 7: AI PDF generated (85%)")
            
            # Step 7: Finalize processing
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Finalizing processing", 95
                )
                
                # Update processing status to completed
                await self.database_service.update_processing_step(
                    file_id, "completed", "Processing completed", 100
                )
                print(f"✅ Step 7: Workflow completed and saved to database (100%)")
            except Exception as db_error:
                print(f"⚠️ Database finalization failed: {db_error}")
                print(f"✅ Step 7: Workflow completed (100%)")
            
            return {
                "success": True,
                "file_id": file_id,
                "original_filename": original_filename,
                "converted_pdf_path": conversion_result["pdf_path"],
                "ai_pdf_path": ai_pdf_path,
                "ai_output": ai_result,  # Include the AI processing results
                "text_content": extracted_text,  # Include the extracted text content
                "processing_status": "completed",
                "message": "CV processing completed successfully"
            }
            
        except Exception as e:
            print(f"❌ Workflow failed at step: {e}")
            
            # Update database with error status (if available)
            try:
                await self.database_service.update_processing_error(file_id, str(e))
            except Exception as db_error:
                print(f"⚠️ Could not save error to database: {db_error}")
            
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e),
                "processing_status": "error",
                "message": f"CV processing failed: {str(e)}"
            }
    
    async def retry_ai_processing(self, file_id: str) -> Dict[str, Any]:
        """
        Retry AI processing for a specific file
        """
        try:
            print(f"🔄 Retrying AI processing for file: {file_id}")
            
            # Reset status for retry (if database available)
            try:
                await self.database_service.reset_for_retry(file_id)
            except Exception as db_error:
                print(f"⚠️ Could not reset database status: {db_error}")
            
            # Get the file info (if database available)
            cv_file = None
            extracted_text = None
            try:
                cv_file = await self.database_service.get_cv_by_file_id(file_id)
                if not cv_file:
                    raise Exception("File not found in database")
                
                # Get the extracted text
                extracted_text = cv_file.get("extractedTextData")
                if not extracted_text:
                    raise Exception("No extracted text found for retry")
            except Exception as db_error:
                print(f"⚠️ Could not retrieve file from database: {db_error}")
                print("📝 Retry will continue with available data")
                # For now, we'll need to have the extracted text available somehow
                # This is a limitation when database is not available
                raise Exception("Database not available for retry - extracted text not accessible")
            
            # Update status (if database available)
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Retrying AI processing", 50
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            # Process with AI
            original_filename = cv_file.get("originalFilename")
            if not original_filename or original_filename == "unknown":
                # Try to get filename from the file path or use a generic name
                raise Exception("Original filename not available for retry - file information is incomplete")
            
            ai_result_info = await self.ai_processor.process_cv_to_json(original_filename, extracted_text)
            
            # Extract the actual AI result and model information
            ai_result = ai_result_info.get("ai_data") if isinstance(ai_result_info, dict) else ai_result_info
            ai_model = ai_result_info.get("model_used", "OpenRouter AI") if isinstance(ai_result_info, dict) else "OpenRouter AI"
            processing_duration_ms = ai_result_info.get("processing_duration_ms", 0) if isinstance(ai_result_info, dict) else 0
            
            # The AI processor returns the CV data directly, not wrapped in a cv_data key
            if not ai_result:
                raise Exception("AI processing failed - no response returned")
            
            # Validate that we have the required personal information
            if not isinstance(ai_result, dict) or "personal_information" not in ai_result:
                raise Exception("AI processing failed - invalid response structure")
            
            # Save AI data (if database available)
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Saving AI data to database", 70
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            try:
                # Convert snake_case keys to camelCase for database compatibility
                converted_cv_data = self._convert_snake_to_camel_case(ai_result)
                
                # Add AI model information to the original response
                ai_result_with_metadata = {
                    **ai_result,
                    "ai_model": ai_model,
                    "processing_duration_ms": processing_duration_ms,
                    "model_used": ai_model
                }
                
                await self.database_service.save_cv_data(
                    file_id, 
                    converted_cv_data,  # Use converted data with camelCase keys
                    ai_model=ai_model,  # Use the actual model that was used
                    processing_duration_ms=processing_duration_ms,  # Use the actual processing duration
                    original_ai_response=ai_result_with_metadata  # Pass AI response with metadata for ai_generated_json
                )
                print(f"✅ AI data saved to database with model {ai_model} (70%)")
            except Exception as db_error:
                print(f"⚠️ Database save failed: {db_error}")
                print(f"📊 CV data available in memory: {list(ai_result.keys())}")
            
            # Generate AI PDF
            try:
                await self.database_service.update_processing_step(
                    file_id, "processing", "Generating AI-based PDF", 85
                )
            except Exception as db_error:
                print(f"⚠️ Database update failed: {db_error}")
            
            # Create output path for AI PDF
            ai_pdf_path = Path("uploads") / f"{file_id}_ai_generated.pdf"
            
            ai_pdf_path = await self.json_converter.convert_json_to_pdf(
                ai_result,  # Use ai_result directly since it contains the CV data
                ai_pdf_path
            )
            
            if not ai_pdf_path:
                raise Exception("AI PDF generation failed")
            
            # Complete processing (if database available)
            try:
                await self.database_service.update_processing_step(
                    file_id, "completed", "Processing completed", 100
                )
                print(f"✅ Retry successful and saved to database for file: {file_id}")
            except Exception as db_error:
                print(f"⚠️ Database finalization failed: {db_error}")
                print(f"✅ Retry successful for file: {file_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "ai_output": ai_result,  # Include the AI processing results
                "ai_pdf_path": ai_pdf_path,  # Include the AI PDF path
                "processing_status": "completed",
                "message": "AI processing retry completed successfully"
            }
            
        except Exception as e:
            print(f"❌ Retry failed: {e}")
            try:
                await self.database_service.update_processing_error(file_id, str(e))
            except Exception as db_error:
                print(f"⚠️ Could not save error to database: {db_error}")
            
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e),
                "processing_status": "error",
                "message": f"Retry failed: {str(e)}"
            }
