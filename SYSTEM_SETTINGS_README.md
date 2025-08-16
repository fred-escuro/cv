# System Settings Implementation

This document describes the implementation of a database-driven system settings system for managing various lists and configurations in the CV Transform application.

## Overview

The system settings allow administrators to manage predefined lists for various form fields such as:
- Gender options
- Civil status options
- Email types
- Phone types
- Skill categories
- Proficiency levels
- Social media platforms

## Database Schema

### Table: `system_generic_settings`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `category` | VARCHAR(100) | Groups related settings (e.g., 'gender', 'civil_status') |
| `setting_key` | VARCHAR(100) | Unique identifier within category |
| `label` | VARCHAR(255) | Human-readable display text |
| `value` | VARCHAR(255) | Optional additional value |
| `sort_order` | INTEGER | Display order within category |
| `is_active` | BOOLEAN | Enable/disable setting |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

## Setup Instructions

### 1. Database Migration

Run the Prisma migration to create the new table:

```bash
cd backend
npx prisma migrate dev --name add_system_settings
```

### 2. Seed Initial Data

Execute the SQL script to populate initial settings:

```bash
cd backend
psql -d your_database_name -f seed_system_settings.sql
```

Or run it through your database management tool.

### 3. Restart Backend

The backend will automatically detect the new table and API endpoints will be available.

## API Endpoints

### Get Settings by Category
```
GET /api/settings/{category}
```

### Get All Settings
```
GET /api/settings
```

### Create Setting
```
POST /api/settings
Body: {
  "category": "gender",
  "setting_key": "non_binary",
  "label": "Non-binary",
  "value": null,
  "sort_order": 5,
  "is_active": true
}
```

### Update Setting
```
PUT /api/settings/{id}
Body: { "label": "Updated Label" }
```

### Delete Setting (Soft Delete)
```
DELETE /api/settings/{id}
```

## Frontend Integration

### TypeAheadDropdown Component

The `TypeAheadDropdown` component provides a searchable dropdown with the following features:

- **Search**: Type to filter options
- **Custom Values**: Allow users to add custom values not in the list
- **Multiple Selection**: Support for selecting multiple values
- **Keyboard Navigation**: Full keyboard support

### Usage Example

```tsx
import { TypeAheadDropdown } from '@/components/ui/typeahead-dropdown';
import { useSystemSettings } from '@/hooks/useSystemSettings';

const MyComponent = () => {
  const { getSettingsByCategory } = useSystemSettings();
  
  return (
    <TypeAheadDropdown
      options={getSettingsByCategory('gender')}
      value={selectedGender}
      onChange={setSelectedGender}
      placeholder="Select gender"
      allowCustom={true}
    />
  );
};
```

### Hook: useSystemSettings

The `useSystemSettings` hook provides:

- `getSettingsByCategory(category)`: Get settings for a specific category
- `getSettingLabel(category, key)`: Get display label for a setting key
- `loading`: Loading state
- `error`: Error state

## Categories and Default Values

### Gender
- male, female, other, prefer_not_to_say

### Civil Status
- single, married, divorced, widowed, separated, civil_partnership

### Email Types
- personal, work, other, academic

### Phone Types
- mobile, home, work, emergency, other

### Skill Categories
- technical, soft, language, framework, database, tool, methodology, certification

### Proficiency Levels
- beginner, intermediate, advanced, expert, master

### Social Platforms
- linkedin, github, twitter, facebook, instagram, youtube, portfolio, blog, other

## Admin Interface

To manage these settings, you can:

1. **Use the API endpoints directly** with tools like Postman
2. **Create a simple admin interface** using the existing API endpoints
3. **Modify the database directly** for bulk operations

## Benefits

1. **Consistency**: All forms use the same predefined options
2. **Maintainability**: Easy to update labels or add new options
3. **Localization**: Support for multiple languages (can be extended)
4. **Data Integrity**: Prevents invalid values from being entered
5. **Scalability**: Easy to add new setting types as needed
6. **User Experience**: Type-ahead search and custom value support

## Future Enhancements

1. **Localization**: Add language-specific labels
2. **Admin UI**: Create a full admin interface for managing settings
3. **Validation Rules**: Add validation for custom values
4. **Audit Trail**: Track who made changes to settings
5. **Import/Export**: Bulk operations for settings management
6. **Environment Support**: Different settings for dev/staging/production

## Troubleshooting

### Common Issues

1. **Settings not loading**: Check if the database table exists and has data
2. **API errors**: Verify the backend is running and the table is accessible
3. **Component not rendering**: Ensure the TypeAheadDropdown component is imported correctly

### Debug Steps

1. Check browser console for errors
2. Verify API endpoints are responding
3. Check database connection and table existence
4. Validate the settings data structure

## Support

For issues or questions about the system settings implementation, check:
1. Backend logs for API errors
2. Database connection status
3. Frontend console for component errors
4. Network tab for API request/response details
