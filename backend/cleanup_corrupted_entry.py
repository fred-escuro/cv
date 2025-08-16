#!/usr/bin/env python3
"""
Script to clean up corrupted database entries
"""

import asyncio
from prisma import Prisma
from datetime import datetime

async def cleanup_corrupted_entries():
    """Clean up corrupted database entries"""
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("🔌 Connected to database")
        
        # Find and delete corrupted entries
        corrupted_files = await prisma.cvfile.find_many(
            where={
                "OR": [
                    {"originalFilename": "unknown"},
                    {"fileHash": "temp_hash"},
                    {"fileHash": "no_hash_available"}
                ]
            }
        )
        
        if corrupted_files:
            print(f"🗑️ Found {len(corrupted_files)} corrupted entries:")
            for file in corrupted_files:
                print(f"  - ID: {file.id}, FileID: {file.fileId}, Filename: '{file.originalFilename}', Hash: '{file.fileHash}'")
            
            # Delete corrupted entries
            for file in corrupted_files:
                try:
                    # First delete related records if they exist
                    await prisma.cvdata.delete_many(where={"fileId": file.fileId})
                    await prisma.personalinfo.delete_many(where={"fileId": file.fileId})
                    await prisma.workexperience.delete_many(where={"fileId": file.fileId})
                    await prisma.education.delete_many(where={"fileId": file.fileId})
                    await prisma.skill.delete_many(where={"fileId": file.fileId})
                    await prisma.certification.delete_many(where={"fileId": file.fileId})
                    await prisma.project.delete_many(where={"fileId": file.fileId})
                    await prisma.awardhonor.delete_many(where={"fileId": file.fileId})
                    await prisma.volunteerexperience.delete_many(where={"fileId": file.fileId})
                    await prisma.reference.delete_many(where={"fileId": file.fileId})
                    await prisma.itsystem.delete_many(where={"fileId": file.fileId})
                    
                    # Then delete the main file record
                    await prisma.cvfile.delete(where={"id": file.id})
                    print(f"✅ Deleted corrupted entry ID {file.id}")
                    
                except Exception as e:
                    print(f"⚠️ Could not delete entry ID {file.id}: {e}")
        else:
            print("✅ No corrupted entries found")
        
        # Also check for any entries with missing or invalid data
        invalid_files = await prisma.cvfile.find_many(
            where={
                "OR": [
                    {"originalFilename": None},
                    {"fileHash": None},
                    {"fileSize": 0}
                ]
            }
        )
        
        if invalid_files:
            print(f"⚠️ Found {len(invalid_files)} entries with invalid data:")
            for file in invalid_files:
                print(f"  - ID: {file.id}, FileID: {file.fileId}, Filename: '{file.originalFilename}', Hash: '{file.fileHash}', Size: {file.fileSize}")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    
    finally:
        await prisma.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    print("🧹 Starting database cleanup...")
    asyncio.run(cleanup_corrupted_entries())
    print("✅ Cleanup completed")
