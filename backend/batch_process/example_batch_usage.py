#!/usr/bin/env python3
"""
Example usage of the Batch CV Processor

This script demonstrates how to use the batch processor programmatically
instead of running it from the command line.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_process.batch_cv_processor import BatchCVProcessor

async def example_batch_processing():
    """Example of how to use the batch processor programmatically"""
    
    # Initialize the processor
    processor = BatchCVProcessor(
        upload_dir="uploads",
        temp_dir="temp"
    )
    
    try:
        # Initialize the processor
        if not await processor.initialize():
            print("❌ Failed to initialize processor")
            return
        
        # Example 1: Process all files in a folder
        print("📁 Example 1: Processing all files in a folder")
        stats = await processor.process_folder(
            folder_path="C:/CVs",  # Replace with your CV folder path
            file_types=None,  # Process all supported file types
            limit=None  # No limit on number of files
        )
        
        print(f"✅ Processed {stats['processed_successfully']} files successfully")
        
        # Example 2: Process only specific file types
        print("\n📁 Example 2: Processing only PDF and DOCX files")
        stats = await processor.process_folder(
            folder_path="C:/CVs",  # Replace with your CV folder path
            file_types=[".pdf", ".docx"],  # Only PDF and DOCX files
            limit=50  # Limit to 50 files
        )
        
        print(f"✅ Processed {stats['processed_successfully']} files successfully")
        
        # Example 3: Process with custom settings
        print("\n📁 Example 3: Custom processing with error handling")
        
        # Reset stats for new processing
        processor.stats = {
            "total_files": 0,
            "processed_successfully": 0,
            "skipped_duplicates": 0,
            "failed_files": 0,
            "errors": []
        }
        
        stats = await processor.process_folder(
            folder_path="C:/CVs",  # Replace with your CV folder path
            file_types=[".pdf"],  # Only PDF files
            limit=10  # Limit to 10 files
        )
        
        # Save detailed log
        await processor.save_log("custom_processing_log.json")
        
        print(f"✅ Processed {stats['processed_successfully']} files successfully")
        print(f"📝 Detailed log saved to: custom_processing_log.json")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await processor.close()

async def example_single_file_processing():
    """Example of processing a single file"""
    
    processor = BatchCVProcessor()
    
    try:
        await processor.initialize()
        
        # Process a single file
        file_path = Path("C:/CVs/example_cv.pdf")  # Replace with actual file path
        
        if file_path.exists():
            result = await processor.process_single_cv(file_path)
            
            if result["success"]:
                print(f"✅ Successfully processed: {result['filename']}")
                if "file_id" in result:
                    print(f"📋 File ID: {result['file_id']}")
            else:
                print(f"❌ Failed to process: {result['filename']}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ File not found: {file_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await processor.close()

async def example_with_error_handling():
    """Example with comprehensive error handling"""
    
    processor = BatchCVProcessor()
    
    try:
        await processor.initialize()
        
        # Process folder with error handling
        folder_path = "C:/CVs"  # Replace with your CV folder path
        
        if not Path(folder_path).exists():
            print(f"❌ Folder not found: {folder_path}")
            return
        
        print(f"🔄 Starting batch processing of: {folder_path}")
        
        stats = await processor.process_folder(
            folder_path=folder_path,
            file_types=[".pdf", ".docx", ".doc"],
            limit=100
        )
        
        # Print detailed results
        print("\n" + "="*60)
        print("📊 DETAILED PROCESSING RESULTS")
        print("="*60)
        
        print(f"📁 Total files found: {stats['total_files']}")
        print(f"✅ Successfully processed: {stats['processed_successfully']}")
        print(f"⏭️  Skipped duplicates: {stats['skipped_duplicates']}")
        print(f"❌ Failed files: {stats['failed_files']}")
        
        if stats['errors']:
            print(f"\n❌ Errors encountered:")
            for i, error in enumerate(stats['errors'], 1):
                print(f"   {i}. {error['filename']}: {error['error']}")
        
        # Calculate success rate
        if stats['total_files'] > 0:
            success_rate = (stats['processed_successfully'] / stats['total_files']) * 100
            print(f"\n📈 Success rate: {success_rate:.1f}%")
        
        # Save log
        await processor.save_log()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await processor.close()

if __name__ == "__main__":
    print("🚀 Batch CV Processor Examples")
    print("="*40)
    
    # Run examples
    asyncio.run(example_batch_processing())
    
    print("\n" + "="*40)
    print("✅ Examples completed!")
    
    # Uncomment the following lines to run other examples:
    # asyncio.run(example_single_file_processing())
    # asyncio.run(example_with_error_handling())
