# Prisma ORM Implementation for CV Transform

This document describes the implementation of Prisma ORM for the CV Transform application, replacing the raw asyncpg approach with a more maintainable and type-safe solution.

## Overview

The Prisma implementation provides:
- **Type Safety**: Full TypeScript-like type safety with Python
- **Auto-generated Client**: Automatically generated database client
- **Schema Management**: Declarative schema definition
- **Migrations**: Easy database schema migrations
- **Relations**: Proper relationship handling between tables
- **Query Building**: Intuitive query building with relations

## Database Schema

The Prisma schema includes the following models:

### Core Tables
- **CvFile**: Main file metadata table
- **CvData**: Original JSON data storage (for future use)

### Normalized Tables
- **PersonalInfo**: Personal information (one-to-one with CvFile)
- **WorkExperience**: Work experience entries (one-to-many with CvFile)
- **Education**: Education entries (one-to-many with CvFile)
- **Skill**: Skills (one-to-many with CvFile)
- **Certification**: Certifications (one-to-many with CvFile)
- **Project**: Projects (one-to-many with CvFile)
- **AwardHonor**: Awards and honors (one-to-many with CvFile)
- **VolunteerExperience**: Volunteer experience (one-to-many with CvFile)
- **Reference**: References (one-to-many with CvFile)
- **ItSystem**: IT systems used (one-to-many with CvFile)

## Setup Instructions

### 1. Install Prisma
```bash
pip install prisma
```

### 2. Initialize Prisma
```bash
prisma init
```

### 3. Configure Environment
Create a `.env` file with your database URL:
```env
DATABASE_URL="postgresql://fredmann:fredmann@localhost:5432/cv"
```

### 4. Generate Prisma Client
```bash
prisma generate
```

### 5. Push Schema to Database
```bash
prisma db push
```

## Usage

### Basic Usage

```python
from services.prisma_database_service import PrismaDatabaseService

# Initialize the service
db_service = PrismaDatabaseService()
await db_service.initialize()

# Save file info
file_hash = await db_service.save_file_info(
    file_id="uuid-here",
    file_path=Path("cv.pdf"),
    original_filename="cv.pdf",
    file_type=".pdf"
)

# Save CV data (automatically populates normalized tables)
await db_service.save_cv_data(
    file_id="uuid-here",
    cv_data=ai_result,
    ai_model="claude-3.5-sonnet",
    processing_duration_ms=1500
)

# Search candidates
candidates = await db_service.search_candidates(
    name="John",
    skills=["Python", "React"],
    job_title="Software Engineer"
)

# Get candidate details
details = await db_service.get_candidate_details("uuid-here")

# Close connection
await db_service.close()
```

### Search Functionality

The Prisma implementation provides powerful search capabilities:

```python
# Search by name
candidates = await db_service.search_candidates(name="John")

# Search by skills
candidates = await db_service.search_candidates(skills=["Python", "React"])

# Search by job title
candidates = await db_service.search_candidates(job_title="Software Engineer")

# Search by company
candidates = await db_service.search_candidates(company="TechCorp")

# Search by location
candidates = await db_service.search_candidates(location="New York")

# Search by education
candidates = await db_service.search_candidates(education_degree="Computer Science")

# Search by certifications
candidates = await db_service.search_candidates(certifications=["AWS", "Google Cloud"])

# Combined search
candidates = await db_service.search_candidates(
    name="John",
    skills=["Python"],
    job_title="Engineer",
    location="California"
)
```

### Statistics and Analytics

```python
# Get processing statistics
stats = await db_service.get_processing_stats()
print(f"Total files: {stats['total_files']}")
print(f"Completed: {stats['completed']}")
print(f"Processing: {stats['processing']}")
print(f"Errors: {stats['errors']}")

# Get skills statistics
skills_stats = await db_service.get_skills_statistics()
print(f"Top technical skills: {skills_stats['technical_skills']}")
print(f"Top soft skills: {skills_stats['soft_skills']}")
print(f"Top languages: {skills_stats['languages']}")
```

## API Endpoints

The following API endpoints are available with the Prisma implementation:

### File Management
- `POST /upload-cv`: Upload and process CV files
- `GET /cv/{file_id}`: Get CV data by file ID
- `GET /cvs`: Get all CVs with pagination
- `DELETE /cv/{file_id}`: Delete CV and associated data

### Search and Analytics
- `GET /search/candidates`: Search candidates with various filters
- `GET /candidate/{file_id}/details`: Get detailed candidate information
- `GET /search/skills-statistics`: Get skills statistics
- `GET /stats`: Get processing statistics

### Database Status
- `GET /db/status`: Get database status and table information

## Benefits of Prisma Implementation

### 1. Type Safety
- Full type checking for database operations
- Auto-completion in IDEs
- Compile-time error detection

### 2. Developer Experience
- Intuitive query building
- Automatic relation handling
- Clear error messages

### 3. Performance
- Optimized queries
- Connection pooling
- Efficient data loading

### 4. Maintainability
- Declarative schema
- Automatic migrations
- Version control friendly

### 5. Scalability
- Easy to add new fields
- Simple to modify relationships
- Efficient indexing

## Migration from asyncpg

The migration from the raw asyncpg implementation to Prisma provides:

1. **Simplified Code**: Less boilerplate code
2. **Better Error Handling**: More descriptive error messages
3. **Type Safety**: Compile-time type checking
4. **Easier Testing**: Better testability with type-safe queries
5. **Future-Proof**: Easy to extend and modify

## Testing

Run the Prisma implementation test:

```bash
python test_prisma_implementation.py
```

This test verifies:
- Database connection
- File upload and processing
- Data storage and retrieval
- Search functionality
- Statistics generation
- Error handling

## Troubleshooting

### Common Issues

1. **Environment Variable Not Found**
   - Ensure `.env` file exists in the backend directory
   - Check that `DATABASE_URL` is properly set

2. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database `cv` exists

3. **Schema Validation Errors**
   - Run `prisma generate` to regenerate client
   - Check schema.prisma for syntax errors
   - Ensure all required fields are defined

4. **Migration Issues**
   - Use `prisma db push` for development
   - Use `prisma migrate dev` for production migrations

### Debugging

Enable Prisma debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Advanced Search**: Full-text search capabilities
2. **Analytics Dashboard**: Real-time analytics
3. **Data Export**: Export functionality
4. **Batch Operations**: Bulk data operations
5. **Caching**: Redis integration for performance

## Conclusion

The Prisma implementation provides a robust, type-safe, and maintainable solution for the CV Transform database operations. It significantly improves the developer experience while maintaining high performance and scalability.
