#!/usr/bin/env python3
"""
Batch CV Processor Script

This script processes multiple CV files from a specified folder and uploads them to the backend.
It runs independently of the UI and handles errors gracefully, skipping problematic files.

Configuration:
    The processor can be configured using a .env file. See env_example.txt for available options.
    Command line arguments override .env settings.

Usage:
    python batch_cv_processor.py [<folder_path>] [--limit <number>] [--file-types <extensions>]

Examples:
    python batch_cv_processor.py                    # Uses .env configuration
    python batch_cv_processor.py "C:/CVs"          # Override folder from .env
    python batch_cv_processor.py --limit 100       # Override limit from .env
    python batch_cv_processor.py --file-types "pdf,docx"  # Override file types from .env
"""

import asyncio
import os
import sys
import argparse
import time
from pathlib import Path
from typing import List, Set, Dict, Any
import aiofiles
import aiohttp
import json
from datetime import datetime
import hashlib

# Add the parent directory to Python path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load the batch_process .env file for OpenRouter API keys and other configuration
# This MUST happen before importing any services that need these environment variables
try:
    from dotenv import load_dotenv
    # Load from current directory (batch_process folder)
    current_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(current_env_path):
        load_dotenv(current_env_path, override=True)  # Use override=True to ensure values are set
        print(f"✅ Loaded batch processor configuration from: {current_env_path}")
        
        # Verify OpenRouter API key is loaded and set it explicitly
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            print(f"✅ OpenRouter API key loaded: {api_key[:10]}...")
            # Ensure the API key is set in the environment
            os.environ['OPENROUTER_API_KEY'] = api_key
            print(f"✅ OpenRouter API key set in environment")
        else:
            print("⚠️ OpenRouter API key not found in .env file")
            print("   Please ensure OPENROUTER_API_KEY is set in your .env file")
    else:
        print(f"⚠️ No .env file found in batch_process directory")
        print("   Please create .env file with OPENROUTER_API_KEY and other settings")
except ImportError:
    print("⚠️ python-dotenv not available, configuration may not load properly")
except Exception as e:
    print(f"⚠️ Error loading configuration: {e}")

# Now import services after environment variables are loaded
from services.workflow_service import WorkflowService
from services.prisma_database_service import PrismaDatabaseService

# Import configuration manager
from config_manager import get_config, get_cv_folder, get_file_limit, get_file_types, get_log_file, get_error_log_file

class BatchCVProcessor:
    """
    Batch processor for CV files that mimics the backend upload process
    """
    
    def __init__(self, upload_dir: str = "uploads", temp_dir: str = "temp", log_dir: str = None):
        # Use absolute paths to ensure files are placed in the correct backend directories
        backend_dir = Path(__file__).parent.parent  # Go up to backend directory
        
        # Set upload directory to backend/uploads (not batch_process/uploads)
        self.upload_dir = Path(backend_dir) / "uploads"
        self.temp_dir = Path(temp_dir)
        self.log_dir = Path(log_dir) if log_dir else Path(get_config().get_log_directory())
        
        # Initialize services with correct paths
        self.workflow_service = WorkflowService()
        self.database_service = PrismaDatabaseService()
        
        # Ensure directories exist
        self.upload_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        print(f"📁 Upload directory set to: {self.upload_dir}")
        print(f"📁 Temp directory set to: {self.temp_dir}")
        print(f"📁 Log directory set to: {self.log_dir}")
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "processed_successfully": 0,
            "skipped_duplicates": 0,
            "failed_files": 0,
            "errors": []
        }
        
        # Detailed processing log
        self.processing_log = []
        
        # Create timestamp for log files
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load configuration
        self.config = get_config()
        
    async def initialize(self):
        """Initialize the processor and database connection"""
        try:
            await self.workflow_service.initialize()
            await self.database_service.initialize()
            print("✅ Batch processor initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize batch processor: {e}")
            return False
    
    async def close(self):
        """Clean up resources"""
        try:
            await self.workflow_service.close()
            await self.database_service.close()
            print("✅ Batch processor closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing batch processor: {e}")
    
    def get_supported_extensions(self) -> Set[str]:
        """Get list of supported file extensions"""
        return set(self.config.get_supported_extensions())
    
    def is_valid_file(self, file_path: Path) -> bool:
        """Check if file is valid for processing"""
        if not file_path.is_file():
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in self.get_supported_extensions():
            return False
        
        # Check file size (skip empty or extremely large files)
        try:
            file_size = file_path.stat().st_size
            min_size = self.config.get_min_file_size()
            max_size = self.config.get_max_file_size()
            
            if file_size == 0:
                return False
            if min_size > 0 and file_size < min_size:
                return False
            if max_size > 0 and file_size > max_size:
                return False
        except OSError:
            return False
        
        return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for duplicate detection"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"⚠️ Could not calculate hash for {file_path.name}: {e}")
            return ""
    
    async def check_duplicate(self, file_path: Path) -> Dict[str, Any]:
        """Check if file already exists in database using multiple methods"""
        try:
            # Method 1: Check by file hash
            file_hash = self.calculate_file_hash(file_path)
            if file_hash:
                existing_file = await self.database_service.check_file_exists_by_hash(file_hash)
                if existing_file:
                    return {
                        "is_duplicate": True,
                        "method": "hash",
                        "existing_file": existing_file,
                        "file_hash": file_hash
                    }
            
            # Method 2: Check by filename (case-insensitive)
            filename = file_path.name.lower()
            existing_file = await self.database_service.check_file_exists_by_filename(filename)
            if existing_file:
                return {
                    "is_duplicate": True,
                    "method": "filename",
                    "existing_file": existing_file,
                    "filename": filename
                }
            
            # Method 3: Check by file path (if available)
            existing_file = await self.database_service.check_file_exists(file_path)
            if existing_file:
                return {
                    "is_duplicate": True,
                    "method": "path",
                    "existing_file": existing_file,
                    "file_path": str(file_path)
                }
            
            return {"is_duplicate": False}
            
        except Exception as e:
            print(f"⚠️ Duplicate check failed: {e}")
            return {"is_duplicate": False, "error": str(e)}
    
    def log_processing_step(self, filename: str, step: str, status: str, details: str = "", error: str = ""):
        """Log a processing step for detailed tracking"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "step": step,
            "status": status,
            "details": details,
            "error": error
        }
        self.processing_log.append(log_entry)
        
        # Also print to console
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️" if status == "warning" else "🔄"
        print(f"{status_icon} {step}: {filename} - {details}")
        if error:
            print(f"   Error: {error}")
    
    async def process_single_cv(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single CV file using the workflow service
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            self.log_processing_step(filename, "START", "info", f"Processing started")
            
            # Step 1: Check if file is duplicate
            self.log_processing_step(filename, "DUPLICATE_CHECK", "info", "Checking for duplicates...")
            duplicate_check = await self.check_duplicate(file_path)
            
            if duplicate_check.get("is_duplicate"):
                method = duplicate_check.get("method", "unknown")
                existing_info = duplicate_check.get("existing_file", {})
                existing_id = existing_info.get("fileId", "unknown")
                
                self.log_processing_step(
                    filename, "DUPLICATE_SKIP", "warning", 
                    f"File already exists in database (ID: {existing_id}, Method: {method})"
                )
                
                self.stats["skipped_duplicates"] += 1
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "duplicate",
                    "method": method,
                    "existing_file_id": existing_id,
                    "processing_time": time.time() - start_time
                }
            
            self.log_processing_step(filename, "DUPLICATE_CHECK", "success", "No duplicates found")
            
            # Step 2: Get file info
            original_filename = file_path.name
            file_type = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            self.log_processing_step(
                filename, "FILE_INFO", "info", 
                f"Type: {file_type}, Size: {file_size / 1024:.1f} KB"
            )
            
            # Step 3: Copy file to upload directory with unique name
            import uuid
            file_id = str(uuid.uuid4())
            safe_filename = original_filename.replace('\\', '_').replace('/', '_').replace(':', '_')
            upload_filename = f"{file_id}_{safe_filename}"
            upload_path = self.upload_dir / upload_filename
            
            # Copy file
            async with aiofiles.open(file_path, 'rb') as src, aiofiles.open(upload_path, 'wb') as dst:
                content = await src.read()
                await dst.write(content)
            
            self.log_processing_step(
                filename, "FILE_COPY", "success", 
                f"Copied to {upload_path}"
            )
            
            # Step 4: Process using workflow service
            self.log_processing_step(filename, "WORKFLOW_PROCESSING", "info", "Starting workflow processing...")
            
            workflow_result = await self.workflow_service.process_cv_workflow(
                upload_path, 
                original_filename, 
                file_type
            )
            
            if workflow_result["success"]:
                self.log_processing_step(
                    filename, "WORKFLOW_PROCESSING", "success", 
                    f"Workflow completed successfully"
                )
                
                self.stats["processed_successfully"] += 1
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "file_id": workflow_result["file_id"],
                    "filename": original_filename,
                    "message": workflow_result["message"],
                    "processing_time": processing_time,
                    "workflow_result": workflow_result
                }
            else:
                error_msg = workflow_result.get('message', 'Unknown error')
                self.log_processing_step(
                    filename, "WORKFLOW_PROCESSING", "error", 
                    f"Workflow failed: {error_msg}"
                )
                
                self.stats["failed_files"] += 1
                processing_time = time.time() - start_time
                
                return {
                    "success": False,
                    "filename": original_filename,
                    "error": error_msg,
                    "processing_time": processing_time
                }
                
        except Exception as e:
            error_msg = str(e)
            self.log_processing_step(
                filename, "PROCESSING_ERROR", "error", 
                f"Unexpected error: {error_msg}"
            )
            
            self.stats["failed_files"] += 1
            self.stats["errors"].append({
                "filename": filename,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "step": "processing"
            })
            
            processing_time = time.time() - start_time
            return {
                "success": False,
                "filename": filename,
                "error": error_msg,
                "processing_time": processing_time
            }
    
    async def process_folder(self, folder_path: str, file_types: List[str] = None, limit: int = None) -> Dict[str, Any]:
        """
        Process all CV files in the specified folder
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")
        
        print(f"📁 Processing folder: {folder_path}")
        print(f"🔍 Looking for files with extensions: {file_types or 'all supported'}")
        if limit:
            print(f"📊 Processing limit: {limit} files")
        
        # Get all files in the folder
        all_files = []
        for file_path in folder.rglob("*"):
            if self.is_valid_file(file_path):
                if file_types is None or file_path.suffix.lower() in file_types:
                    all_files.append(file_path)
        
        # Apply limit if specified
        if limit and len(all_files) > limit:
            all_files = all_files[:limit]
            print(f"📊 Limited to {limit} files")
        
        self.stats["total_files"] = len(all_files)
        print(f"📊 Found {len(all_files)} files to process")
        
        if not all_files:
            print("⚠️ No valid files found to process")
            return self.stats
        
        # Process files
        start_time = time.time()
        for i, file_path in enumerate(all_files, 1):
            print(f"\n📋 [{i}/{len(all_files)}] Processing: {file_path.name}")
            
            try:
                result = await self.process_single_cv(file_path)
                
                # Add small delay to prevent overwhelming the system
                delay = self.config.get_processing_delay()
                if delay > 0:
                    await asyncio.sleep(delay)
                
            except Exception as e:
                error_msg = f"Unexpected error processing {file_path.name}: {e}"
                print(f"❌ {error_msg}")
                
                self.stats["failed_files"] += 1
                self.stats["errors"].append({
                    "filename": file_path.name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "step": "main_loop"
                })
                
                self.log_processing_step(
                    file_path.name, "MAIN_LOOP_ERROR", "error", 
                    f"Error in main processing loop: {e}"
                )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Print summary
        self.print_summary(processing_time)
        
        return self.stats
    
    def print_summary(self, processing_time: float):
        """Print processing summary"""
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
        print(f"📁 Total files found: {self.stats['total_files']}")
        print(f"✅ Successfully processed: {self.stats['processed_successfully']}")
        print(f"⏭️  Skipped duplicates: {self.stats['skipped_duplicates']}")
        print(f"❌ Failed files: {self.stats['failed_files']}")
        
        if self.stats["errors"]:
            print(f"\n❌ Errors encountered:")
            for error in self.stats["errors"][:5]:  # Show first 5 errors
                print(f"   - {error['filename']}: {error['error']}")
            if len(self.stats["errors"]) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more errors")
        
        # Calculate success rate
        if self.stats["total_files"] > 0:
            success_rate = (self.stats["processed_successfully"] / self.stats["total_files"]) * 100
            print(f"\n📈 Success rate: {success_rate:.1f}%")
        
        print("="*60)
    
    async def save_log(self, log_file: str = None):
        """Save comprehensive processing log to file"""
        if log_file is None:
            default_name = self.config.get_log_file()
            log_file = f"{default_name}_{self.timestamp}.json"
        
        log_path = self.log_dir / log_file
        
        try:
            # Prepare comprehensive log data
            log_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "processor_version": "1.0.0",
                    "upload_dir": str(self.upload_dir),
                    "temp_dir": str(self.temp_dir),
                    "log_dir": str(self.log_dir)
                },
                "summary": {
                    "stats": self.stats,
                    "total_processing_time": sum(entry.get("processing_time", 0) for entry in self.processing_log if "processing_time" in entry),
                    "files_processed": len(self.processing_log)
                },
                "detailed_log": self.processing_log,
                "configuration": {
                    "supported_extensions": list(self.get_supported_extensions()),
                    "max_file_size_mb": 100,
                    "processing_delay_seconds": 0.5
                }
            }
            
            async with aiofiles.open(log_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(log_data, indent=2, ensure_ascii=False))
            
            print(f"📝 Comprehensive log saved to: {log_path}")
            
            # Also save a simplified summary log
            summary_log = f"batch_summary_{self.timestamp}.json"
            summary_path = self.log_dir / summary_log
            
            summary_data = {
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "upload_dir": str(self.upload_dir),
                "temp_dir": str(self.temp_dir)
            }
            
            async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(summary_data, indent=2, ensure_ascii=False))
            
            print(f"📝 Summary log saved to: {summary_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save log: {e}")
    
    async def save_error_log(self, error_log_file: str = None):
        """Save detailed error log for failed files"""
        if not self.stats["errors"]:
            return
        
        if error_log_file is None:
            default_name = self.config.get_error_log_file()
            error_log_file = f"{default_name}_{self.timestamp}.json"
        
        error_log_path = self.log_dir / error_log_file
        
        try:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "total_errors": len(self.stats["errors"]),
                "errors": self.stats["errors"]
            }
            
            async with aiofiles.open(error_log_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(error_data, indent=2, ensure_ascii=False))
            
            print(f"📝 Error log saved to: {error_log_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save error log: {e}")

async def main():
    """Main function to run the batch processor"""
    parser = argparse.ArgumentParser(description="Batch CV Processor")
    parser.add_argument("folder_path", nargs='?', help="Path to folder containing CV files (overrides .env setting)")
    parser.add_argument("--limit", type=int, help="Maximum number of files to process (overrides .env setting)")
    parser.add_argument("--file-types", help="Comma-separated list of file extensions (e.g., pdf,docx,doc) (overrides .env setting)")
    parser.add_argument("--log-file", help="Path to save processing log (overrides .env setting)")
    parser.add_argument("--error-log", help="Path to save error log (overrides .env setting)")
    parser.add_argument("--show-config", action="store_true", help="Show current configuration and exit")
    parser.add_argument("--create-env", action="store_true", help="Create .env template file and exit")
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.show_config:
        config = get_config()
        config.print_configuration()
        return
    
    # Create .env template if requested
    if args.create_env:
        config = get_config()
        config.create_env_template()
        return
    
    # Get configuration values (command line args override .env)
    folder_path = args.folder_path or get_cv_folder()
    file_limit = args.limit if args.limit is not None else get_file_limit()
    log_file = args.log_file or get_log_file()
    error_log = args.error_log or get_error_log_file()
    
    # Parse file types
    file_types = None
    if args.file_types:
        file_types = [f".{ext.strip().lower()}" for ext in args.file_types.split(",")]
        print(f"🔍 File types filter (command line): {file_types}")
    else:
        file_types = get_file_types()
        if file_types:
            print(f"🔍 File types filter (.env): {file_types}")
        else:
            print("🔍 File types filter: All supported")
    
    # Validate folder path
    if not folder_path or not Path(folder_path).exists():
        print(f"❌ Error: Invalid folder path: {folder_path}")
        print("   Please specify a valid folder path or set DEFAULT_CV_FOLDER in .env file")
        return
    
    print(f"📁 Processing folder: {folder_path}")
    if file_limit > 0:
        print(f"📊 File limit: {file_limit}")
    else:
        print("📊 File limit: No limit")
    
    # Initialize processor
    processor = BatchCVProcessor()
    
    try:
        # Initialize
        if not await processor.initialize():
            print("❌ Failed to initialize processor. Exiting.")
            return
        
        # Process folder
        await processor.process_folder(
            folder_path=folder_path,
            file_types=file_types,
            limit=file_limit
        )
        
        # Save logs
        await processor.save_log(log_file)
        await processor.save_error_log(error_log)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await processor.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
