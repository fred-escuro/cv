#!/usr/bin/env python3
"""
Database seeding script for system_generic_settings table
"""

import asyncio
import os
from prisma import Prisma

# Initial data to seed
INITIAL_SETTINGS = [
    # Gender options
    {'category': 'gender', 'settingKey': 'male', 'label': 'Male', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'gender', 'settingKey': 'female', 'label': 'Female', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'gender', 'settingKey': 'other', 'label': 'Other', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'gender', 'settingKey': 'prefer_not_to_say', 'label': 'Prefer not to say', 'value': None, 'sortOrder': 4, 'isActive': True},
    
    # Civil status options
    {'category': 'civil_status', 'settingKey': 'single', 'label': 'Single', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'civil_status', 'settingKey': 'married', 'label': 'Married', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'civil_status', 'settingKey': 'divorced', 'label': 'Divorced', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'civil_status', 'settingKey': 'widowed', 'label': 'Widowed', 'value': None, 'sortOrder': 4, 'isActive': True},
    {'category': 'civil_status', 'settingKey': 'separated', 'label': 'Separated', 'value': None, 'sortOrder': 5, 'isActive': True},
    {'category': 'civil_status', 'settingKey': 'civil_partnership', 'label': 'Civil Partnership', 'value': None, 'sortOrder': 6, 'isActive': True},
    
    # Email types
    {'category': 'email_types', 'settingKey': 'personal', 'label': 'Personal Email', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'email_types', 'settingKey': 'work', 'label': 'Work Email', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'email_types', 'settingKey': 'other', 'label': 'Other Email', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'email_types', 'settingKey': 'academic', 'label': 'Academic Email', 'value': None, 'sortOrder': 4, 'isActive': True},
    
    # Phone types
    {'category': 'phone_types', 'settingKey': 'mobile', 'label': 'Mobile', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'phone_types', 'settingKey': 'home', 'label': 'Home', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'phone_types', 'settingKey': 'work', 'label': 'Work', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'phone_types', 'settingKey': 'emergency', 'label': 'Emergency', 'value': None, 'sortOrder': 4, 'isActive': True},
    {'category': 'phone_types', 'settingKey': 'other', 'label': 'Other', 'value': None, 'sortOrder': 5, 'isActive': True},
    
    # Skill categories
    {'category': 'skill_categories', 'settingKey': 'technical', 'label': 'Technical Skills', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'soft', 'label': 'Soft Skills', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'language', 'label': 'Languages', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'framework', 'label': 'Frameworks & Libraries', 'value': None, 'sortOrder': 4, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'database', 'label': 'Databases', 'value': None, 'sortOrder': 5, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'tool', 'label': 'Development Tools', 'value': None, 'sortOrder': 6, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'methodology', 'label': 'Methodologies', 'value': None, 'sortOrder': 7, 'isActive': True},
    {'category': 'skill_categories', 'settingKey': 'certification', 'label': 'Certifications', 'value': None, 'sortOrder': 8, 'isActive': True},
    
    # Proficiency levels
    {'category': 'proficiency_levels', 'settingKey': 'beginner', 'label': 'Beginner', 'value': '1', 'sortOrder': 1, 'isActive': True},
    {'category': 'proficiency_levels', 'settingKey': 'intermediate', 'label': 'Intermediate', 'value': '2', 'sortOrder': 2, 'isActive': True},
    {'category': 'proficiency_levels', 'settingKey': 'advanced', 'label': 'Advanced', 'value': '3', 'sortOrder': 3, 'isActive': True},
    {'category': 'proficiency_levels', 'settingKey': 'expert', 'label': 'Expert', 'value': '4', 'sortOrder': 4, 'isActive': True},
    {'category': 'proficiency_levels', 'settingKey': 'master', 'label': 'Master', 'value': '5', 'sortOrder': 5, 'isActive': True},
    
    # Social media platforms
    {'category': 'social_platforms', 'settingKey': 'linkedin', 'label': 'LinkedIn', 'value': None, 'sortOrder': 1, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'github', 'label': 'GitHub', 'value': None, 'sortOrder': 2, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'twitter', 'label': 'Twitter/X', 'value': None, 'sortOrder': 3, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'facebook', 'label': 'Facebook', 'value': None, 'sortOrder': 4, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'instagram', 'label': 'Instagram', 'value': None, 'sortOrder': 5, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'youtube', 'label': 'YouTube', 'value': None, 'sortOrder': 6, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'portfolio', 'label': 'Portfolio Website', 'value': None, 'sortOrder': 7, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'blog', 'label': 'Blog', 'value': None, 'sortOrder': 8, 'isActive': True},
    {'category': 'social_platforms', 'settingKey': 'other', 'label': 'Other', 'value': None, 'sortOrder': 9, 'isActive': True},
]

async def seed_database():
    """Seed the database with initial system settings"""
    prisma = Prisma()
    
    try:
        print("🔌 Connecting to database...")
        await prisma.connect()
        print("✅ Connected to database")
        
        # Check if settings already exist
        existing_count = await prisma.systemgenericsetting.count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} settings. Skipping seed.")
            return
        
        print("🌱 Seeding database with initial system settings...")
        
        # Insert all settings
        for setting_data in INITIAL_SETTINGS:
            await prisma.systemgenericsetting.create(data=setting_data)
            print(f"✅ Added: {setting_data['category']} - {setting_data['label']}")
        
        print(f"🎉 Successfully seeded {len(INITIAL_SETTINGS)} system settings!")
        
        # Verify the data
        total_count = await prisma.systemgenericsetting.count()
        print(f"📊 Total settings in database: {total_count}")
        
        # Show summary by category
        categories = await prisma.systemgenericsetting.group_by(
            by=['category'],
            _count={'category': True}
        )
        
        print("\n📋 Settings by category:")
        for cat in categories:
            print(f"  • {cat.category}: {cat._count['category']} items")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await prisma.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    print("🚀 Starting database seeding...")
    asyncio.run(seed_database())
    print("✨ Seeding completed!")
