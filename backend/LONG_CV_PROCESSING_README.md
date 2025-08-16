# CV Processing Guide

## Overview

The CV Transform system processes CV documents by sending the entire CV to the AI in one request, with intelligent handling of AI response truncation. This approach ensures the AI sees the complete context while handling any response length limitations.

## How It Works

### 1. Complete CV Processing
- The entire CV document is sent to the AI in one request
- AI sees complete context and all information
- This ensures better understanding of relationships between sections

### 2. Enhanced Token Management
- Higher token limits are allocated for AI responses
- Dynamic token calculation based on CV length
- Prevents truncation in most cases

### 3. AI Response Truncation Handling
- If AI response is truncated, automatic repair is attempted
- Multiple repair strategies: JSON completion, extraction, syntax fixing
- Ensures valid JSON output even from truncated responses

### 4. Fallback and Retry Logic
- Multiple AI models are tried if one fails
- Retry logic handles temporary failures
- Comprehensive error handling and recovery

## Configuration

### AI Model Settings
```python
AI_MODEL_CONFIG = {
    "MODEL_TOKEN_LIMITS": {
        'anthropic/claude-3.5-sonnet': 200000,
        'openai/gpt-4o': 128000,
        'anthropic/claude-3-haiku': 200000,
        'meta-llama/llama-3.1-8b-instruct': 8192,
    },
    "DEFAULT_MAX_TOKENS": 8000,
    "MIN_MAX_TOKENS": 2000,
    "SAFETY_BUFFER_TOKENS": 1000,
    "TEMPERATURE": 0.1,
}
```

### Processing Settings
```python
PROCESSING_CONFIG = {
    "ENABLE_DETAILED_LOGGING": True,
    "MAX_CHUNK_RETRIES": 2,
    "AI_API_TIMEOUT": 180,  # Seconds
    "ENABLE_FALLBACK_MODELS": True,
}
```

## Usage

### Automatic Processing
CVs are processed automatically - no changes needed to your existing workflow:

1. Upload a CV document (any length)
2. The entire CV is sent to AI in one request
3. Processing happens automatically in the background
4. Results are returned with full context preserved

### Manual Configuration
You can adjust settings by modifying `config.py`:

```python
# Adjust timeout for very long CVs
PROCESSING_CONFIG["AI_API_TIMEOUT"] = 300  # 5 minutes

# Reduce retry attempts
PROCESSING_CONFIG["MAX_CHUNK_RETRIES"] = 1

# Change temperature for AI responses
AI_MODEL_CONFIG["TEMPERATURE"] = 0.05
```

## Testing

### Test AI Processing
```bash
cd backend
python test_ai_processor.py
```

### Test JSON Truncation Handling
```bash
cd backend
python test_json_truncation.py
```

## Performance Considerations

### Processing Time
- Long CVs take proportionally longer to process
- Each chunk requires a separate AI API call
- Typical processing time: 2-5 seconds per chunk
- 100K character CV ≈ 3-4 chunks ≈ 6-20 seconds total

### API Costs
- Each chunk consumes AI API tokens
- Longer CVs = more API calls = higher costs
- Consider chunk size vs. cost trade-offs

### Memory Usage
- Text is processed in chunks to minimize memory usage
- Temporary files are cleaned up automatically
- Peak memory usage remains low regardless of CV length

## Error Handling

### Chunk Processing Failures
- Individual chunk failures don't stop the entire process
- Failed chunks are retried up to 2 times (configurable)
- If all retries fail, the chunk is skipped
- Final result includes data from successful chunks

### AI Model Failures
- Multiple fallback models are tried automatically
- If all models fail, detailed error information is returned
- Error messages include which models were attempted

### Timeout Handling
- API calls have configurable timeouts (default: 120 seconds)
- Long CVs may require longer timeouts
- Adjust `AI_API_TIMEOUT` in config if needed

## Monitoring and Logging

### Log Output
The system provides detailed logging during processing:

```
📊 Processing CV: long_cv.pdf
📏 Text length: 125000 characters
📋 Text is long (125000 chars), using chunked processing...
📋 Split into 4 chunks
🔄 Processing chunk 1/4 (35000 chars)
🤖 Trying model 1/4: anthropic/claude-3.5-sonnet
📊 Token calculation for anthropic/claude-3.5-sonnet:
   Model limit: 200000
   Estimated prompt tokens: 8750
   Max response tokens: 8000
✅ Successfully processed with model: anthropic/claude-3.5-sonnet
🔄 Processing chunk 2/4 (32000 chars)
...
🔗 Merging 4 chunk results...
✅ JSON processing completed successfully for long_cv.pdf
```

### Debug Information
- Text length and chunk count
- Model selection and token calculations
- Processing progress for each chunk
- Merge results and final status

## Troubleshooting

### Common Issues

#### 1. Chunks Too Small
**Problem**: CVs are split into many tiny chunks
**Solution**: Increase `MIN_CHUNK_SIZE` in config

#### 2. Processing Timeouts
**Problem**: AI API calls timeout on long CVs
**Solution**: Increase `AI_API_TIMEOUT` in config

#### 3. Memory Issues
**Problem**: System runs out of memory on very long CVs
**Solution**: Reduce `MAX_CHUNK_SIZE` in config

#### 4. Incomplete Results
**Problem**: Some information is missing from final output
**Solution**: Check chunk overlap and increase if needed

### Performance Optimization

#### For Very Long CVs (>200K characters)
```python
TEXT_PROCESSING_CONFIG["MAX_CHUNK_SIZE"] = 60000
TEXT_PROCESSING_CONFIG["CHUNK_OVERLAP"] = 3000
PROCESSING_CONFIG["AI_API_TIMEOUT"] = 180
```

#### For Faster Processing
```python
TEXT_PROCESSING_CONFIG["MAX_CHUNK_SIZE"] = 30000
PROCESSING_CONFIG["MAX_CHUNK_RETRIES"] = 1
AI_MODEL_CONFIG["DEFAULT_MAX_TOKENS"] = 4000
```

#### For Maximum Accuracy
```python
TEXT_PROCESSING_CONFIG["CHUNK_OVERLAP"] = 5000
PROCESSING_CONFIG["MAX_CHUNK_RETRIES"] = 3
AI_MODEL_CONFIG["TEMPERATURE"] = 0.05
```

## Best Practices

### 1. Chunk Size Selection
- **Small chunks (20-30K)**: Better for complex, detailed CVs
- **Large chunks (40-60K)**: Better for simple, structured CVs
- **Overlap**: 2-5K characters usually provides good context

### 2. Model Selection
- **Claude models**: Better for long, complex documents
- **GPT models**: Faster processing, good for structured content
- **Fallback models**: Ensure processing continues if primary fails

### 3. Error Handling
- Always check processing logs for warnings
- Monitor chunk success rates
- Adjust configuration based on failure patterns

### 4. Cost Optimization
- Balance chunk size vs. API call count
- Use appropriate models for document complexity
- Monitor token usage and costs

## Future Enhancements

### Planned Features
- **Smart chunking**: AI-powered text segmentation
- **Parallel processing**: Process multiple chunks simultaneously
- **Adaptive chunking**: Dynamic chunk size based on content
- **Progress tracking**: Real-time processing status updates

### Customization Options
- **Content-aware chunking**: Preserve section boundaries
- **Language-specific processing**: Optimize for different languages
- **Industry-specific parsing**: Specialized CV formats

## Support

For issues or questions about long CV processing:

1. Check the logs for detailed error information
2. Verify configuration settings
3. Test with the provided test scripts
4. Review this documentation for troubleshooting steps

The system is designed to handle CVs of any length automatically, but configuration adjustments may be needed for optimal performance with very long documents.
