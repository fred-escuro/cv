# CV Text Lines Migration Guide

## Overview

This migration adds full-text search capabilities to the CV system by storing individual text lines from extracted CV content. This allows users to search through the actual text content of CVs, even if the AI processing missed some important information.

## What's New

### 1. **Database Schema Changes**
- New `cv_text_lines` table for storing individual text lines
- Full-text search indexes using PostgreSQL GIN
- Trigram indexes for partial matching
- Foreign key relationships with cascade delete

### 2. **New Services**
- `TextLineProcessor`: Processes extracted text into searchable lines
- Enhanced `PrismaDatabaseService` with text line methods
- Updated `WorkflowService` to include text line processing

### 3. **API Endpoints**
- `GET /api/search/cv-text` - Full-text search
- `GET /api/search/cv-text-partial` - Partial text matching
- `GET /api/search/cv-context/{file_id}/{line_number}` - Get context around a line
- `GET /api/cv/{file_id}/text-lines` - Get all text lines for a CV

### 4. **Frontend Component**
- `CVTextSearch` component for searching CV content
- Support for both full-text and partial matching
- Rich result display with line types and context

## Migration Steps

### 1. **Database Migration**

Run the new migration to create the `cv_text_lines` table:

```bash
cd backend
# The migration file is already created at:
# prisma/migrations/20250115000000_add_cv_text_lines/migration.sql
```

### 2. **Update Prisma Schema**

The schema has been updated with:
- New `CvTextLine` model
- Updated `CvFile` model with `textLines` relation

### 3. **Regenerate Prisma Client**

```bash
cd backend
prisma generate
```

### 4. **Restart Backend Service**

The backend will now automatically process text lines for all new CV uploads.

## How It Works

### 1. **Text Processing Pipeline**

```
CV Upload → Text Extraction → Text Line Processing → Database Storage
     ↓              ↓              ↓                    ↓
   PDF/DOCX    Raw Text    Individual Lines    Searchable Index
```

### 2. **Text Line Classification**

The system automatically classifies text lines into types:
- **header**: ALL CAPS lines (likely section headers)
- **list_item**: Numbered or bulleted items
- **key_value**: Lines with colon separators
- **contact_info**: Email addresses
- **date_info**: Date-related content
- **content**: General text content

### 3. **Search Capabilities**

#### Full-Text Search
- Uses PostgreSQL full-text search with GIN indexes
- Supports complex queries with ranking
- Language-aware stemming and ranking

#### Partial Matching
- Uses trigram similarity for fuzzy matching
- Useful for finding partial text matches
- Handles typos and OCR errors

## Usage Examples

### 1. **Full-Text Search**

```typescript
// Search for specific skills
const results = await fetch('/api/search/cv-text?q=Python React Node.js');
const data = await results.json();
```

### 2. **Partial Matching**

```typescript
// Find similar text (handles typos, OCR errors)
const results = await fetch('/api/search/cv-text-partial?term=Pyton');
const data = await results.json();
```

### 3. **Get Context**

```typescript
// Get surrounding lines for context
const context = await fetch('/api/search/cv-context/file-id/15?context=5');
const data = await context.json();
```

### 4. **Get All Text Lines**

```typescript
// Get all text lines for a specific CV
const textLines = await fetch('/api/cv/file-id/text-lines?limit=200');
const data = await textLines.json();
```

## Frontend Integration

### 1. **Add to Dashboard**

```tsx
import { CVTextSearch } from '@/components/CVTextSearch';

// Add to your dashboard or search page
<CVTextSearch />
```

### 2. **Custom Search Integration**

```tsx
const searchCVText = async (query: string) => {
  const response = await fetch(`/api/search/cv-text?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  return data.results;
};
```

## Performance Considerations

### 1. **Indexing**
- Full-text search indexes are created automatically
- Trigram indexes may take time to build for large datasets
- Consider running during off-peak hours

### 2. **Storage**
- Each CV typically generates 50-200 text lines
- Text lines are automatically cleaned and optimized
- Old text lines are cleaned up when CVs are deleted

### 3. **Search Performance**
- Full-text search: O(log n) with GIN indexes
- Partial matching: O(n) but optimized with trigram indexes
- Results are limited to prevent performance issues

## Troubleshooting

### 1. **Migration Issues**

If the migration fails:

```bash
# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log

# Verify pg_trgm extension
psql -d your_database -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### 2. **Search Not Working**

- Verify the `cv_text_lines` table exists
- Check that text lines are being created for new CVs
- Ensure PostgreSQL full-text search is enabled

### 3. **Performance Issues**

- Monitor index usage: `EXPLAIN ANALYZE` on search queries
- Consider adding additional indexes for specific use cases
- Monitor table size and cleanup old data if needed

## Future Enhancements

### 1. **Advanced Search**
- Boolean search operators
- Field-specific search (search only headers, skills, etc.)
- Search within specific CV categories

### 2. **Analytics**
- Search term analytics
- Popular search patterns
- CV content insights

### 3. **Machine Learning**
- Automatic text line classification improvement
- Search result ranking optimization
- Content similarity detection

## API Reference

### Search Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search/cv-text` | GET | Full-text search across all CVs |
| `/api/search/cv-text-partial` | GET | Partial text matching |
| `/api/search/cv-context/{file_id}/{line_number}` | GET | Get context around a line |
| `/api/cv/{file_id}/text-lines` | GET | Get all text lines for a CV |

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query for full-text search |
| `term` | string | Search term for partial matching |
| `limit` | integer | Maximum number of results (default: 50) |
| `context` | integer | Number of context lines (default: 3) |

### Response Format

```json
{
  "success": true,
  "results": [
    {
      "file_id": "uuid",
      "line_number": 15,
      "line_text": "Python Developer with 5 years experience",
      "line_type": "content",
      "original_filename": "john_doe_cv.pdf",
      "rank": 0.876,
      "similarity_score": 0.95
    }
  ]
}
```

## Support

For issues or questions about the CV text lines migration:

1. Check the backend logs for error messages
2. Verify database connectivity and permissions
3. Ensure all dependencies are properly installed
4. Check that the migration completed successfully

The system is designed to be robust and will continue working even if text line processing fails for individual CVs.
