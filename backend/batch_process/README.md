# Batch CV Processor

The Batch CV Processor is a standalone script that can process multiple CV files from a folder and upload them to the backend without affecting the current UI process. It's designed to handle large volumes of CVs efficiently while providing detailed logging and error handling.

## Features

- ✅ **Batch Processing**: Process multiple CV files from a folder
- ✅ **Error Handling**: Skip problematic files and continue processing
- ✅ **Duplicate Detection**: Automatically skip files that already exist
- ✅ **Progress Tracking**: Real-time progress updates and statistics
- ✅ **Detailed Logging**: Comprehensive logs for debugging and auditing
- ✅ **Configurable**: Customize file types, limits, and processing options
- ✅ **UI Independent**: Runs separately from the web interface
- ✅ **Resume Capability**: Can resume processing from where it left off

## Supported File Types

- **Documents**: PDF, DOC, DOCX, RTF, TXT, JSON
- **Images**: JPG, JPEG, PNG, BMP, TIFF

## Prerequisites

1. **Python 3.8+** installed
2. **Backend services** running (database, workflow service)
3. **Required Python packages** installed (see requirements.txt)
4. **CV files** in a folder ready for processing

## Installation

1. Ensure you're in the backend directory
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Usage

#### Basic Usage
```bash
cd batch_process
python batch_cv_processor.py "C:/CVs"
```

#### Process Specific File Types
```bash
cd batch_process
python batch_cv_processor.py "C:/CVs" --file-types "pdf,docx,doc"
```

#### Limit Number of Files
```bash
cd batch_process
python batch_cv_processor.py "C:/CVs" --limit 100
```

#### Custom Log File
```bash
cd batch_process
python batch_cv_processor.py "C:/CVs" --log-file "my_processing_log.json"
```

#### Complete Example
```bash
cd batch_process
python batch_cv_processor.py "C:/CVs" --limit 50 --file-types "pdf,docx" --log-file "batch_log.json"
```

### Programmatic Usage

```python
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_process.batch_cv_processor import BatchCVProcessor

async def process_cvs():
    processor = BatchCVProcessor()
    
    try:
        await processor.initialize()
        
        stats = await processor.process_folder(
            folder_path="C:/CVs",
            file_types=[".pdf", ".docx"],
            limit=100
        )
        
        print(f"Processed {stats['processed_successfully']} files successfully")
        
    finally:
        await processor.close()

# Run the processor
asyncio.run(process_cvs())
```

## Configuration

The batch processor can be configured by modifying `batch_processor_config.py`:

```python
# File size limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MIN_FILE_SIZE = 1024  # 1KB

# Processing settings
PROCESSING_DELAY = 0.5  # Delay between files
BATCH_SIZE = 50  # Process files in batches

# Error handling
SKIP_CORRUPTED_FILES = True
CONTINUE_ON_ERROR = True
MAX_ERRORS_BEFORE_STOP = 100
```

## Output and Logging

### Console Output
The script provides real-time progress updates with detailed step-by-step logging:
```
📁 Processing folder: C:/CVs
🔍 Looking for files with extensions: all supported
📊 Found 150 files to process

📋 [1/150] Processing: cv_john_doe.pdf
🔄 START: cv_john_doe.pdf - Processing started
🔄 DUPLICATE_CHECK: cv_john_doe.pdf - Checking for duplicates...
✅ DUPLICATE_CHECK: cv_john_doe.pdf - No duplicates found
🔄 FILE_INFO: cv_john_doe.pdf - Type: .pdf, Size: 245.3 KB
✅ FILE_COPY: cv_john_doe.pdf - Copied to uploads/abc123_cv_john_doe.pdf
🔄 WORKFLOW_PROCESSING: cv_john_doe.pdf - Starting workflow processing...
✅ WORKFLOW_PROCESSING: cv_john_doe.pdf - Workflow completed successfully

📋 [2/150] Processing: cv_jane_smith.docx
🔄 START: cv_jane_smith.docx - Processing started
🔄 DUPLICATE_CHECK: cv_jane_smith.docx - Checking for duplicates...
⚠️ DUPLICATE_SKIP: cv_jane_smith.docx - File already exists in database (ID: abc123, Method: hash)
```

### Log Files
The script automatically generates **three types** of comprehensive logs:

#### 1. Comprehensive Log (`batch_processing_log_YYYYMMDD_HHMMSS.json`)
Complete audit trail with every processing step:
```json
{
  "metadata": {
    "timestamp": "2025-01-15T10:30:00.123456",
    "processor_version": "1.0.0",
    "upload_dir": "uploads",
    "temp_dir": "temp",
    "log_dir": "logs"
  },
  "summary": {
    "stats": {
      "total_files": 150,
      "processed_successfully": 145,
      "skipped_duplicates": 3,
      "failed_files": 2,
      "errors": []
    },
    "total_processing_time": 7200.5,
    "files_processed": 150
  },
  "detailed_log": [
    {
      "timestamp": "2025-01-15T10:30:01.123456",
      "filename": "cv_john_doe.pdf",
      "step": "START",
      "status": "info",
      "details": "Processing started",
      "error": ""
    }
  ],
  "configuration": {
    "supported_extensions": [".pdf", ".doc", ".docx", ".rtf", ".txt", ".json", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
    "max_file_size_mb": 100,
    "processing_delay_seconds": 0.5
  }
}
```

#### 2. Summary Log (`batch_summary_YYYYMMDD_HHMMSS.json`)
Quick overview of processing results:
```json
{
  "timestamp": "2025-01-15T10:30:00.123456",
  "stats": {
    "total_files": 150,
    "processed_successfully": 145,
    "skipped_duplicates": 3,
    "failed_files": 2,
    "errors": []
  },
  "upload_dir": "uploads",
  "temp_dir": "temp"
}
```

#### 3. Error Log (`batch_error_log_YYYYMMDD_HHMMSS.json`)
Detailed error information for failed files:
```json
{
  "timestamp": "2025-01-15T10:30:00.123456",
  "total_errors": 2,
  "errors": [
    {
      "filename": "corrupted_cv.pdf",
      "error": "File is corrupted and cannot be processed",
      "timestamp": "2025-01-15T10:35:00.123456",
      "step": "processing"
    }
  ]
}
```

## Error Handling

The batch processor handles various error scenarios gracefully:

### File-Level Errors
- **Corrupted files**: Skipped with error logged
- **Unsupported formats**: Skipped automatically
- **Permission issues**: Logged and skipped
- **File size issues**: Skipped if too large/small

### Duplicate Detection and Handling
The processor uses **three methods** to detect and skip duplicate CVs:

1. **Hash-based Detection** (Most Reliable)
   - Calculates SHA-256 hash of file content
   - Identifies exact file duplicates regardless of filename
   - Automatically skips files with matching hashes

2. **Filename-based Detection** (Case-insensitive)
   - Checks if filename already exists in database
   - Useful for detecting renamed duplicates
   - Skips files with matching names

3. **Path-based Detection** (Fallback)
   - Uses existing file path checking methods
   - Additional safety check for duplicates

**Duplicate files are automatically skipped** and processing continues with the next file, ensuring no time is wasted on already-processed CVs.

### System-Level Errors
- **Database connection issues**: Retries with exponential backoff
- **Disk space issues**: Stops processing and logs error
- **Memory issues**: Processes files in smaller batches

### Processing Errors
- **AI processing failures**: Logged and file marked as failed
- **Conversion errors**: Logged and file marked as failed
- **Text extraction failures**: Logged and file marked as failed

## Performance Considerations

### Processing Speed
- **Sequential processing**: ~1-2 files per minute (depending on file size and complexity)
- **Memory usage**: Low memory footprint, processes one file at a time
- **Disk I/O**: Minimal impact, only copies files to upload directory

### Optimization Tips
1. **Use SSD storage** for better I/O performance
2. **Process during off-peak hours** to avoid system slowdown
3. **Limit batch size** for very large folders
4. **Monitor system resources** during processing

## Monitoring and Debugging

### Real-Time Monitoring
```bash
# Watch the processing in real-time
cd batch_process
python batch_cv_processor.py "C:/CVs" | tee processing.log
```

### Debug Mode
Enable detailed logging by modifying the configuration:
```python
LOG_LEVEL = "DEBUG"
SHOW_DETAILED_OUTPUT = True
```

### Check Processing Status
The script provides progress indicators:
- File count and progress
- Success/failure statistics
- Error details and counts
- Processing time estimates

## Troubleshooting

### Common Issues

#### Database Connection Errors
```
❌ Failed to initialize batch processor: Database connection failed
```
**Solution**: Ensure the backend database is running and accessible

#### File Permission Errors
```
❌ Error processing cv_file.pdf: Permission denied
```
**Solution**: Check file permissions and ensure the script has read access

#### Memory Issues
```
❌ Error processing large_file.pdf: Memory allocation failed
```
**Solution**: Reduce batch size or process smaller files first

#### Duplicate Detection Issues
```
⚠️ Duplicate check failed: Database query timeout
```
**Solution**: Check database performance and increase timeout values

### Performance Issues

#### Slow Processing
- Check if other processes are using the system
- Verify disk I/O performance
- Monitor database query performance

#### High Memory Usage
- Reduce batch size
- Process files in smaller groups
- Monitor system resources

## Integration with Existing System

### Database Integration
- Uses the same database service as the UI
- Maintains data consistency
- Respects existing duplicate detection logic

### File System Integration
- Uses the same upload directory structure
- Maintains file naming conventions
- Integrates with existing cleanup processes

### Workflow Integration
- Uses the same workflow service as individual uploads
- Maintains processing consistency
- Generates the same output formats

## Security Considerations

### File Access
- Only reads files from specified folders
- No network access to external systems
- Respects file system permissions

### Data Privacy
- Processes files locally
- No data sent to external services
- Logs contain only file names and error messages

### System Security
- Runs with minimal privileges
- No elevation of permissions
- Safe error handling prevents system compromise

## Future Enhancements

### Planned Features
- **Parallel processing** for faster batch operations
- **Resume capability** for interrupted processing
- **Email notifications** for completion status
- **Webhook integration** for external system updates
- **Progress persistence** across script restarts

### Customization Options
- **Custom file filters** based on content
- **Priority processing** for specific file types
- **Scheduled processing** at specific times
- **Integration with external systems**

## Support and Maintenance

### Getting Help
1. Check the console output for error messages
2. Review the generated log files
3. Verify system requirements and dependencies
4. Check file permissions and accessibility

### Maintenance
- Regularly clean up log files
- Monitor disk space usage
- Update dependencies as needed
- Backup configuration files

### Updates
- Keep the script updated with backend changes
- Monitor for new file format support
- Update error handling as needed
- Maintain compatibility with database schema changes

## License

This batch processor is part of the CV Transform application and follows the same licensing terms.

---

For additional support or questions, please refer to the main application documentation or contact the development team.
