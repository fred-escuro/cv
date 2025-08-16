#!/usr/bin/env python3
"""
Prisma-based database service for CV data storage
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from prisma import Prisma
from prisma.models import (
    CvFile, PersonalInfo, WorkExperience, Education, 
    Skill, Certification, Project, AwardHonor, VolunteerExperience, 
    Reference, ItSystem, Email, Phone, SocialUrl, SystemGenericSetting
)

class PrismaDatabaseService:
    """
    Service to handle PostgreSQL database operations for CV data storage using Prisma ORM
    """
    
    def __init__(self):
        self.prisma = Prisma()
        self._is_connected = False
    
    async def initialize(self):
        """Initialize Prisma client connection"""
        try:
            await self.prisma.connect()
            self._is_connected = True
            print("✅ Prisma database connection established successfully")
            
        except Exception as e:
            print(f"❌ Prisma database connection failed: {e}")
            raise
    
    async def close(self):
        """Close Prisma client connection"""
        if self._is_connected:
            await self.prisma.disconnect()
            self._is_connected = False
            print("🔌 Prisma database connection closed")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def check_file_exists(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check if a file already exists in the database by hash"""
        file_hash = self._calculate_file_hash(file_path)
        print(f"🔍 Checking file hash: {file_hash}")
        
        # Check if file exists by hash
        existing_file = await self.prisma.cvfile.find_first(
            where={"fileHash": file_hash},
            include={
                "personalInfo": True,
                "workExperience": True,
                "education": True,
                "skills": True,
                "certifications": True,
                "projects": True,
                "awardsHonors": True,
                "volunteerExperience": True,
                "references": True,
                "itSystems": True
            }
        )
        
        if existing_file:
            print(f"✅ Found existing file with hash {file_hash}")
            print(f"   - File ID: {existing_file.fileId}")
            print(f"   - Original filename: {existing_file.originalFilename}")
            return existing_file.model_dump()
        else:
            print(f"❌ No existing file found with hash {file_hash}")
        return None
    
    async def check_file_exists_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Check if a file already exists in the database by hash string"""
        try:
            existing_file = await self.prisma.cvfile.find_first(
                where={"fileHash": file_hash},
                include={
                    "personalInfo": True,
                    "workExperience": True,
                    "education": True,
                    "skills": True,
                    "certifications": True,
                    "projects": True,
                    "awardsHonors": True,
                    "volunteerExperience": True,
                    "references": True,
                    "itSystems": True
                }
            )
            
            if existing_file:
                print(f"✅ Found existing file with hash {file_hash}")
                print(f"   - File ID: {existing_file.fileId}")
                print(f"   - Original filename: {existing_file.originalFilename}")
                return existing_file.model_dump()
            else:
                print(f"❌ No existing file found with hash {file_hash}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error checking file by hash: {e}")
            return None
    
    async def check_file_exists_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Check if a file already exists in the database by filename (case-insensitive)"""
        try:
            existing_file = await self.prisma.cvfile.find_first(
                where={
                    "originalFilename": {
                        "mode": "insensitive",
                        "equals": filename
                    }
                },
                include={
                    "personalInfo": True,
                    "workExperience": True,
                    "education": True,
                    "skills": True,
                    "certifications": True,
                    "projects": True,
                    "awardsHonors": True,
                    "volunteerExperience": True,
                    "references": True,
                    "itSystems": True
                }
            )
            
            if existing_file:
                print(f"✅ Found existing file with filename {filename}")
                print(f"   - File ID: {existing_file.fileId}")
                print(f"   - Original filename: {existing_file.originalFilename}")
                return existing_file.model_dump()
            else:
                print(f"❌ No existing file found with filename {filename}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error checking file by filename: {e}")
            return None
    
    async def save_file_info(self, file_id: str, file_path: Path, original_filename: str, file_type: str) -> str:
        """Save file information to the database"""
        file_size = file_path.stat().st_size
        file_hash = self._calculate_file_hash(file_path)
        
        # Create a new file record with the given file_id
        cv_file = await self.prisma.cvfile.create(
            data={
                "fileId": file_id,
                "originalFilename": original_filename,
                "fileType": file_type,
                "fileSize": file_size,
                "fileHash": file_hash,
                "processingStatus": "processing",
                "currentStep": "File uploaded",
                "progressPercent": 10
            }
        )
        
        print(f"✅ Created CV file record with ID: {cv_file.id}")
        return file_hash
    
    async def update_converted_pdf_info(self, file_id: str, converted_pdf_filename: str, extracted_text_data: str):
        """Update the converted PDF filename and extracted text data"""
        try:
            # Only update existing records, don't create new ones
            await self.prisma.cvfile.update(
                where={"fileId": file_id},
                data={
                    "convertedPdfFilename": converted_pdf_filename,
                    "extractedTextData": extracted_text_data,
                    "updatedAt": datetime.now()
                }
            )
        except Exception as e:
            print(f"⚠️ Could not update converted PDF info for file {file_id}: {e}")
            # Don't create a new record with default values
            raise e
    
    async def save_cv_data(self, file_id: str, cv_data: Dict[str, Any], ai_model: str = None, processing_duration_ms: int = None, original_ai_response: Dict[str, Any] = None):
        """Save CV data to the database using Prisma"""
        try:
            print(f"💾 Saving CV data to database for file_id: {file_id}")
            print(f"📊 CV data keys: {list(cv_data.keys())}")
            
            # Use original AI response for ai_generated_json if provided, otherwise use cv_data
            json_to_save = original_ai_response if original_ai_response is not None else cv_data
            print(f"📊 JSON to save to ai_generated_json keys: {list(json_to_save.keys())}")
            
            # Ensure json_to_save is a valid JSON-serializable object
            import json
            try:
                # Test if the data can be serialized to JSON
                json.dumps(json_to_save)
            except (TypeError, ValueError) as e:
                print(f"⚠️ JSON data is not serializable: {e}")
                # Convert any non-serializable objects to strings
                json_to_save = self._make_json_serializable(json_to_save)
            
            # First, ensure the cv_files record exists
            existing_file = await self.prisma.cvfile.find_unique(where={"fileId": file_id})
            if not existing_file:
                print(f"❌ CV file record not found for file_id: {file_id}")
                raise Exception(f"CV file record not found for file_id: {file_id}")
            
            print(f"✅ Found CV file record: {existing_file.id}")
            
            # Save the complete AI response to the aiGeneratedJson column using raw SQL
            # This bypasses Prisma's JSON type validation issues
            json_string = json.dumps(json_to_save)
            await self.prisma.query_raw("""
                UPDATE cv_files 
                SET ai_generated_json = $1::jsonb, updated_at = NOW()
                WHERE file_id = $2::uuid
            """, json_string, file_id)
            
            print("✅ AI generated JSON saved successfully")
            print(f"📊 Saved JSON size: {len(json_string)} characters")
            
            # Save normalized data to separate tables (using camelCase keys)
            try:
                await self._save_normalized_data(file_id, cv_data)
                print("✅ Normalized data saved successfully")
            except Exception as e:
                print(f"⚠️ Warning: Failed to save normalized data: {e}")
                print(f"🔍 Normalized data error type: {type(e)}")
                print(f"🔍 Normalized data error details: {str(e)}")
                # Continue with the process even if normalized data fails
                # The main JSON data is already saved
            
            # Update processing status to completed
            await self.prisma.cvfile.update(
                where={"fileId": file_id},
                data={
                    "processingStatus": "completed",
                    "currentStep": "Processing completed",
                    "progressPercent": 100,
                    "updatedAt": datetime.now()
                }
            )
            
            print(f"✅ CV data saved successfully to database for file_id: {file_id}")
            
        except Exception as e:
            print(f"❌ Error saving CV data to database: {e}")
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON serializable format"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert any other type to string
            return str(obj)
    
    async def _save_normalized_data(self, file_id: str, cv_data: Dict[str, Any]):
        """Save CV data to normalized tables for better searchability"""
        try:
            # Validate file_id is a valid UUID
            import uuid
            try:
                uuid.UUID(file_id)
            except ValueError:
                raise ValueError(f"Invalid file_id format: {file_id}")
            
            # Clear existing normalized data for this file_id
            await self._clear_normalized_data(file_id)
            
            # Save personal information (using camelCase keys)
            if cv_data.get('personalInformation'):
                await self._save_personal_info(file_id, cv_data.get('personalInformation', {}))
            
            # Save work experience (using camelCase keys)
            if cv_data.get('workExperience'):
                await self._save_work_experience(file_id, cv_data.get('workExperience', []))
            
            # Save education (using camelCase keys)
            if cv_data.get('education'):
                await self._save_education(file_id, cv_data.get('education', []))
            
            # Save skills (using camelCase keys)
            if cv_data.get('skills'):
                await self._save_skills(file_id, cv_data.get('skills', {}))
            
            # Save certifications (using camelCase keys)
            if cv_data.get('certifications'):
                await self._save_certifications(file_id, cv_data.get('certifications', []))
            
            # Save projects (using camelCase keys)
            if cv_data.get('projects'):
                await self._save_projects(file_id, cv_data.get('projects', []))
            
            # Save awards and honors (using camelCase keys)
            if cv_data.get('awardsAndHonors'):
                await self._save_awards_honors(file_id, cv_data.get('awardsAndHonors', []))
            
            # Save volunteer experience (using camelCase keys)
            if cv_data.get('volunteerExperience'):
                await self._save_volunteer_experience(file_id, cv_data.get('volunteerExperience', []))
            
            # Save references (using camelCase keys)
            if cv_data.get('references'):
                await self._save_references(file_id, cv_data.get('references', []))
            
            # Save IT systems (using camelCase keys)
            if cv_data.get('itSystemUsed'):
                await self._save_it_systems(file_id, cv_data.get('itSystemUsed', []))
            
            print(f"✅ Normalized data saved for file_id: {file_id}")
            
        except Exception as e:
            print(f"❌ Error saving normalized data: {e}")
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Error details: {str(e)}")
            raise
    
    async def _clear_normalized_data(self, file_id: str):
        """Clear existing normalized data for a file_id"""
        # Delete all related normalized data
        await self.prisma.personalinfo.delete_many(where={"fileId": file_id})
        await self.prisma.workexperience.delete_many(where={"fileId": file_id})
        await self.prisma.education.delete_many(where={"fileId": file_id})
        await self.prisma.skill.delete_many(where={"fileId": file_id})
        await self.prisma.certification.delete_many(where={"fileId": file_id})
        await self.prisma.project.delete_many(where={"fileId": file_id})
        await self.prisma.awardhonor.delete_many(where={"fileId": file_id})
        await self.prisma.volunteerexperience.delete_many(where={"fileId": file_id})
        await self.prisma.reference.delete_many(where={"fileId": file_id})
        await self.prisma.itsystem.delete_many(where={"fileId": file_id})
        # Note: emails, phones, and socialUrls are automatically deleted due to CASCADE
    
    def _clean_string_field(self, value):
        """Clean and validate string fields, converting empty strings to None"""
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned == '' or cleaned.lower() in ['n/a', 'na', 'none', 'null', 'undefined']:
                return None
            return cleaned
        return str(value) if value else None

    async def _save_personal_info(self, file_id: str, personal_info: Dict[str, Any]):
        """Save personal information to normalized table"""
        if not personal_info:
            return
            
        # Handle address
        address = personal_info.get('address', {})
        desired_location = personal_info.get('desiredLocation', {})
        work_preference = personal_info.get('workPreference', {})
        
        # Handle dates
        birth_date = self._parse_date(personal_info.get('birthDate'))
        
        # Handle civil status - ensure it's a string, not an array
        civil_status = personal_info.get('civilStatus')
        if isinstance(civil_status, list):
            civil_status = civil_status[0] if civil_status else None
        
        # Create the main personal info record
        await self.prisma.personalinfo.create(
            data={
                "fileId": file_id,
                "firstName": self._clean_string_field(personal_info.get('firstName')),
                "middleName": self._clean_string_field(personal_info.get('middleName')),
                "lastName": self._clean_string_field(personal_info.get('lastName')),
                "birthDate": birth_date,
                "gender": self._clean_string_field(personal_info.get('gender')),
                "civilStatus": self._clean_string_field(civil_status),
                "street": self._clean_string_field(address.get('street')),
                "barangay": self._clean_string_field(address.get('barangay')),
                "city": self._clean_string_field(address.get('city')),
                "state": self._clean_string_field(address.get('state')),
                "postalCode": self._clean_string_field(address.get('postalCode')),
                "country": self._clean_string_field(address.get('country')),
                "desiredCity": self._clean_string_field(desired_location.get('city')),
                "desiredState": self._clean_string_field(desired_location.get('state')),
                "desiredCountry": self._clean_string_field(desired_location.get('country')),
                "openToWorkFromHome": bool(work_preference.get('openToWorkFromHome')) if work_preference.get('openToWorkFromHome') is not None else None,
                "openToWorkOnsite": bool(work_preference.get('openToWorkOnsite')) if work_preference.get('openToWorkOnsite') is not None else None,
            }
        )
        
        # Save emails as separate records
        emails = personal_info.get('emails', [])
        if emails and isinstance(emails, list):
            for i, email_data in enumerate(emails):
                if email_data:
                    email_value = email_data if isinstance(email_data, str) else email_data.get('email', str(email_data))
                    email_type = email_data.get('type', 'personal') if isinstance(email_data, dict) else 'personal'
                    
                    cleaned_email = self._clean_string_field(email_value)
                    if cleaned_email:
                        await self.prisma.email.create(
                            data={
                                "fileId": file_id,
                                "email": cleaned_email,
                                "emailType": self._clean_string_field(email_type),
                                "isPrimary": i == 0  # First email is primary
                            }
                        )
        
        # Save phones as separate records
        phones = personal_info.get('phones', [])
        if phones and isinstance(phones, list):
            for i, phone_data in enumerate(phones):
                if phone_data:
                    if isinstance(phone_data, dict):
                        phone_value = phone_data.get('number')
                        phone_type = phone_data.get('type', 'mobile')
                    else:
                        phone_value = str(phone_data)
                        phone_type = 'mobile'
                    
                    cleaned_phone = self._clean_string_field(phone_value)
                    cleaned_phone_type = self._clean_string_field(phone_type)
                    
                    if cleaned_phone:
                        await self.prisma.phone.create(
                            data={
                                "fileId": file_id,
                                "phone": cleaned_phone,
                                "phoneType": cleaned_phone_type,
                                "isPrimary": i == 0  # First phone is primary
                            }
                        )
        
        # Save social URLs as separate records
        social_urls = personal_info.get('socialUrls', [])
        if social_urls and isinstance(social_urls, list):
            for social_url_data in social_urls:
                if social_url_data:
                    if isinstance(social_url_data, dict):
                        url_value = social_url_data.get('url') or social_url_data.get('link')
                        platform = social_url_data.get('platform') or social_url_data.get('type')
                    else:
                        url_value = str(social_url_data)
                        platform = self._extract_platform_from_url(url_value)
                    
                    cleaned_url = self._clean_string_field(url_value)
                    cleaned_platform = self._clean_string_field(platform)
                    
                    if cleaned_url:
                        await self.prisma.socialurl.create(
                            data={
                                "fileId": file_id,
                                "url": cleaned_url,
                                "platform": cleaned_platform
                            }
                        )
    
    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from social media URL"""
        if not url:
            return None
        
        url_lower = url.lower()
        if 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'github.com' in url_lower:
            return 'github'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'youtube.com' in url_lower:
            return 'youtube'
        elif 'medium.com' in url_lower:
            return 'medium'
        elif 'stackoverflow.com' in url_lower:
            return 'stackoverflow'
        else:
            return 'other'
    
    async def _save_work_experience(self, file_id: str, work_experience: List[Dict[str, Any]]):
        """Save work experience to normalized table"""
        for exp in work_experience:
            if not exp:
                continue
                
            start_date = self._parse_date(exp.get('startDate'))
            end_date = self._parse_date(exp.get('endDate'))
            is_current = exp.get('endDate', '').lower() in ['present', 'current', 'ongoing']
            
            await self.prisma.workexperience.create(
                data={
                    "fileId": file_id,
                    "jobTitle": self._clean_string_field(exp.get('jobTitle')),
                    "companyName": self._clean_string_field(exp.get('companyName')),
                    "location": self._clean_string_field(exp.get('location')),
                    "startDate": start_date,
                    "endDate": end_date,
                    "isCurrent": is_current,
                    "responsibilities": [self._clean_string_field(resp) for resp in exp.get('responsibilities', []) if resp and self._clean_string_field(resp)]
                }
            )
    
    async def _save_education(self, file_id: str, education: List[Dict[str, Any]]):
        """Save education to normalized table"""
        for edu in education:
            if not edu:
                continue
                
            start_date = self._parse_date(edu.get('startDate'))
            end_date = self._parse_date(edu.get('endDate'))
            
            # Handle GPA field - convert empty strings to None, validate numeric values
            gpa = edu.get('gpa')
            if gpa is not None:
                if isinstance(gpa, str):
                    gpa = gpa.strip()
                    if gpa == '' or gpa.lower() in ['n/a', 'na', 'none', 'null']:
                        gpa = None
                    else:
                        try:
                            gpa = float(gpa)
                        except (ValueError, TypeError):
                            gpa = None
                elif isinstance(gpa, (int, float)):
                    gpa = float(gpa)
                else:
                    gpa = None
            
            await self.prisma.education.create(
                data={
                    "fileId": file_id,
                    "degree": self._clean_string_field(edu.get('degree')),
                    "institution": self._clean_string_field(edu.get('institution')),
                    "location": self._clean_string_field(edu.get('location')),
                    "startDate": start_date,
                    "endDate": end_date,
                    "gpa": gpa,
                    "honors": self._clean_string_field(edu.get('honors'))
                }
            )
    
    async def _save_skills(self, file_id: str, skills: Dict[str, Any]):
        """Save skills to normalized table"""
        # Technical skills
        technical_skills = skills.get('technicalSkills', [])
        for skill in technical_skills:
            cleaned_skill = self._clean_string_field(skill)
            if cleaned_skill:
                await self.prisma.skill.create(
                    data={
                        "fileId": file_id,
                        "skillName": cleaned_skill,
                        "skillType": "technical"
                    }
                )
        
        # Soft skills
        soft_skills = skills.get('softSkills', [])
        for skill in soft_skills:
            cleaned_skill = self._clean_string_field(skill)
            if cleaned_skill:
                await self.prisma.skill.create(
                    data={
                        "fileId": file_id,
                        "skillName": cleaned_skill,
                        "skillType": "soft"
                    }
                )
        
        # Computer languages
        computer_languages = skills.get('computerLanguages', [])
        for lang in computer_languages:
            if lang and isinstance(lang, dict):
                cleaned_language = self._clean_string_field(lang.get('language'))
                cleaned_proficiency = self._clean_string_field(lang.get('proficiency'))
                if cleaned_language:
                    await self.prisma.skill.create(
                        data={
                            "fileId": file_id,
                            "skillName": cleaned_language,
                            "skillType": "language",
                            "proficiency": cleaned_proficiency
                        }
                    )
    
    async def _save_certifications(self, file_id: str, certifications: List[Dict[str, Any]]):
        """Save certifications to normalized table"""
        for cert in certifications:
            if not cert:
                continue
                
            issue_date = self._parse_date(cert.get('issueDate'))
            expiration_date = self._parse_date(cert.get('expirationDate'))
            
            await self.prisma.certification.create(
                data={
                    "fileId": file_id,
                    "name": self._clean_string_field(cert.get('name')),
                    "issuingOrganization": self._clean_string_field(cert.get('issuingOrganization')),
                    "issueDate": issue_date,
                    "expirationDate": expiration_date
                }
            )
    
    async def _save_projects(self, file_id: str, projects: List[Dict[str, Any]]):
        """Save projects to normalized table"""
        for project in projects:
            if not project:
                continue
                
            start_date = self._parse_date(project.get('startDate'))
            end_date = self._parse_date(project.get('endDate'))
            
            await self.prisma.project.create(
                data={
                    "fileId": file_id,
                    "title": self._clean_string_field(project.get('title')),
                    "description": self._clean_string_field(project.get('description')),
                    "startDate": start_date,
                    "endDate": end_date,
                    "projectUrl": self._clean_string_field(project.get('projectUrl')),
                    "technologies": [self._clean_string_field(tech) for tech in project.get('technologiesUsed', []) if tech and self._clean_string_field(tech)]
                }
            )
    
    async def _save_awards_honors(self, file_id: str, awards: List[Dict[str, Any]]):
        """Save awards and honors to normalized table"""
        for award in awards:
            if not award:
                continue
                
            date_received = self._parse_date(award.get('dateReceived'))
            
            await self.prisma.awardhonor.create(
                data={
                    "fileId": file_id,
                    "title": self._clean_string_field(award.get('title')),
                    "issuingOrganization": self._clean_string_field(award.get('issuingOrganization')),
                    "dateReceived": date_received,
                    "description": self._clean_string_field(award.get('description'))
                }
            )
    
    async def _save_volunteer_experience(self, file_id: str, volunteer: List[Dict[str, Any]]):
        """Save volunteer experience to normalized table"""
        for vol in volunteer:
            if not vol:
                continue
                
            start_date = self._parse_date(vol.get('startDate'))
            end_date = self._parse_date(vol.get('endDate'))
            
            await self.prisma.volunteerexperience.create(
                data={
                    "fileId": file_id,
                    "role": self._clean_string_field(vol.get('role')),
                    "organization": self._clean_string_field(vol.get('organization')),
                    "location": self._clean_string_field(vol.get('location')),
                    "startDate": start_date,
                    "endDate": end_date,
                    "description": self._clean_string_field(vol.get('description'))
                }
            )
    
    async def _save_references(self, file_id: str, references: List[Dict[str, Any]]):
        """Save references to normalized table"""
        for ref in references:
            if not ref:
                continue
                
            await self.prisma.reference.create(
                data={
                    "fileId": file_id,
                    "name": self._clean_string_field(ref.get('name')),
                    "relationship": self._clean_string_field(ref.get('relationship')),
                    "email": self._clean_string_field(ref.get('email')),
                    "phone": self._clean_string_field(ref.get('phone'))
                }
            )
    
    async def _save_it_systems(self, file_id: str, it_systems: List[Dict[str, Any]]):
        """Save IT systems to normalized table"""
        for system in it_systems:
            if not system:
                continue
                
            await self.prisma.itsystem.create(
                data={
                    "fileId": file_id,
                    "systemName": self._clean_string_field(system.get('nameOfSystem')),
                    "abbreviation": self._clean_string_field(system.get('abbreviation'))
                }
            )
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing']:
            return None
            
        try:
            # Handle YYYY-MM format
            if len(date_str) == 7 and date_str[4] == '-':
                return datetime.strptime(date_str + '-01', '%Y-%m-%d')
            # Handle YYYY-MM-DD format
            elif len(date_str) == 10:
                return datetime.strptime(date_str, '%Y-%m-%d')
            # Handle YYYY format
            elif len(date_str) == 4:
                return datetime.strptime(date_str + '-01-01', '%Y-%m-%d')
            else:
                return None
        except:
            return None
    
    async def update_processing_error(self, file_id: str, error_message: str):
        """Update processing status to error"""
        await self.prisma.cvfile.update(
            where={"fileId": file_id},
            data={
                "processingStatus": "error",
                "currentStep": "Error occurred",
                "progressPercent": 0,
                "errorMessage": error_message,
                "updatedAt": datetime.now()
            }
        )
    
    async def update_processing_step(self, file_id: str, status: str, step: str, progress: int):
        """Update processing status, current step, and progress"""
        await self.prisma.cvfile.update(
            where={"fileId": file_id},
            data={
                "processingStatus": status,
                "currentStep": step,
                "progressPercent": progress,
                "updatedAt": datetime.now()
            }
        )
    
    async def get_processing_progress(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get real-time processing progress for a CV file"""
        try:
            cv_file = await self.prisma.cvfile.find_first(
                where={"fileId": file_id},
                include={
                    "personalInfo": True,
                    "workExperience": True,
                    "education": True,
                    "skills": True,
                    "certifications": True,
                    "projects": True,
                    "awardsHonors": True,
                    "volunteerExperience": True,
                    "references": True,
                    "itSystems": True
                }
            )
            
            if not cv_file:
                return None
            
            # Get AI model information from the CV data
            ai_model = "Unknown"
            processing_duration_ms = 0
            
            # Check if we have AI-generated data
            if hasattr(cv_file, 'aiGeneratedJson') and cv_file.aiGeneratedJson:
                try:
                    ai_data = json.loads(cv_file.aiGeneratedJson)
                    if isinstance(ai_data, dict):
                        # Extract AI model info if available
                        ai_model = ai_data.get('ai_model', 'OpenRouter AI')
                        processing_duration_ms = ai_data.get('processing_duration_ms', 0)
                except:
                    ai_model = "OpenRouter AI"
            
            return {
                "status": cv_file.processingStatus,
                "current_step": cv_file.currentStep,
                "progress": cv_file.progressPercent,
                "error": cv_file.errorMessage if hasattr(cv_file, 'errorMessage') else None,
                "ai_model": ai_model,
                "processing_duration_ms": processing_duration_ms,
                "date_created": cv_file.dateCreated,
                "date_modified": cv_file.updatedAt
            }
            
        except Exception as e:
            print(f"❌ Error getting processing progress: {e}")
            return None
    
    async def update_cv_data(self, file_id: str, cv_data: Dict[str, Any]) -> bool:
        """Update CV data including personal info, work experience, education, etc."""
        try:
            # Start a transaction to update all related data
            async with self.prisma.tx() as transaction:
                # Update or create personal info
                if "personalInfo" in cv_data:
                    personal_info_data = cv_data["personalInfo"]
                    
                    # Check if personal info exists
                    existing_personal_info = await transaction.personalinfo.find_first(
                        where={"fileId": file_id}
                    )
                    
                    if existing_personal_info:
                        # Update existing personal info
                        await transaction.personalinfo.update(
                            where={"id": existing_personal_info.id},
                                                            data={
                                    "firstName": personal_info_data.get("firstName"),
                                    "middleName": personal_info_data.get("middleName"),
                                    "lastName": personal_info_data.get("lastName"),
                                    "birthDate": self._parse_date(personal_info_data.get("birthDate")),
                                    "gender": personal_info_data.get("gender"),
                                    "civilStatus": personal_info_data.get("civilStatus"),
                                    "street": personal_info_data.get("street"),
                                    "barangay": personal_info_data.get("barangay"),
                                    "city": personal_info_data.get("city"),
                                    "state": personal_info_data.get("state"),
                                    "postalCode": personal_info_data.get("postalCode"),
                                    "country": personal_info_data.get("country"),
                                    "desiredCity": personal_info_data.get("desiredCity"),
                                    "desiredState": personal_info_data.get("desiredState"),
                                    "desiredCountry": personal_info_data.get("desiredCountry"),
                                    "openToWorkFromHome": personal_info_data.get("openToWorkFromHome", False),
                                    "openToWorkOnsite": personal_info_data.get("openToWorkOnsite", False),
                                }
                        )
                    else:
                        # Create new personal info
                        await transaction.personalinfo.create(
                            data={
                                "fileId": file_id,
                                "firstName": personal_info_data.get("firstName"),
                                "middleName": personal_info_data.get("middleName"),
                                "lastName": personal_info_data.get("lastName"),
                                "birthDate": self._parse_date(personal_info_data.get("birthDate")),
                                "gender": personal_info_data.get("gender"),
                                "civilStatus": personal_info_data.get("civilStatus"),
                                "street": personal_info_data.get("street"),
                                "barangay": personal_info_data.get("barangay"),
                                "city": personal_info_data.get("city"),
                                "state": personal_info_data.get("state"),
                                "postalCode": personal_info_data.get("postalCode"),
                                "country": personal_info_data.get("country"),
                                "desiredCity": personal_info_data.get("desiredCity"),
                                "desiredState": personal_info_data.get("desiredState"),
                                "desiredCountry": personal_info_data.get("desiredCountry"),
                                "openToWorkFromHome": personal_info_data.get("openToWorkFromHome", False),
                                "openToWorkOnsite": personal_info_data.get("openToWorkOnsite", False),
                            }
                        )
                    
                    # Update emails
                    if "emails" in personal_info_data and existing_personal_info:
                        # Delete existing emails
                        await transaction.email.delete_many(where={"fileId": file_id})
                        # Create new emails
                        for email_data in personal_info_data["emails"]:
                            if email_data.get("email"):
                                await transaction.email.create(
                                    data={
                                        "fileId": file_id,
                                        "email": email_data["email"],
                                        "emailType": email_data.get("emailType", "personal"),
                                        "isPrimary": email_data.get("isPrimary", False)
                                    }
                                )
                    
                    # Update phones
                    if "phones" in personal_info_data and existing_personal_info:
                        # Delete existing phones
                        await transaction.phone.delete_many(where={"fileId": file_id})
                        # Create new phones
                        for phone_data in personal_info_data["phones"]:
                            if phone_data.get("phone"):
                                await transaction.phone.create(
                                    data={
                                        "fileId": file_id,
                                        "phone": phone_data["phone"],
                                        "phoneType": phone_data.get("phoneType", "mobile"),
                                        "isPrimary": phone_data.get("isPrimary", False)
                                    }
                                )
                    
                    # Update social URLs
                    if "socialUrls" in personal_info_data and existing_personal_info:
                        # Delete existing social URLs
                        await transaction.socialurl.delete_many(where={"fileId": file_id})
                        # Create new social URLs
                        for social_data in personal_info_data["socialUrls"]:
                            if social_data.get("url"):
                                await transaction.socialurl.create(
                                    data={
                                        "fileId": file_id,
                                        "url": social_data["url"],
                                        "platform": social_data.get("platform", "")
                                    }
                                )
                
                # Update work experience
                if "workExperience" in cv_data:
                    # Delete existing work experience
                    await transaction.workexperience.delete_many(where={"fileId": file_id})
                    # Create new work experience
                    for exp_data in cv_data["workExperience"]:
                        if exp_data.get("jobTitle"):
                            await transaction.workexperience.create(
                                data={
                                    "fileId": file_id,
                                    "jobTitle": exp_data["jobTitle"],
                                    "companyName": exp_data.get("companyName"),
                                    "location": exp_data.get("location"),
                                    "startDate": self._parse_date(exp_data.get("startDate")),
                                    "endDate": self._parse_date(exp_data.get("endDate")),
                                    "isCurrent": exp_data.get("isCurrent", False),
                                    "responsibilities": exp_data.get("responsibilities", [])
                                }
                            )
                
                # Update education
                if "education" in cv_data:
                    # Delete existing education
                    await transaction.education.delete_many(where={"fileId": file_id})
                    # Create new education
                    for edu_data in cv_data["education"]:
                        if edu_data.get("degree"):
                            await transaction.education.create(
                                data={
                                    "fileId": file_id,
                                    "degree": edu_data["degree"],
                                    "institution": edu_data.get("institution"),
                                    "location": edu_data.get("location"),
                                    "startDate": self._parse_date(edu_data.get("startDate")),
                                    "endDate": self._parse_date(edu_data.get("endDate")),
                                    "gpa": edu_data.get("gpa"),
                                    "honors": edu_data.get("honors")
                                }
                            )
                
                # Update skills
                if "skills" in cv_data:
                    # Delete existing skills
                    await transaction.skill.delete_many(where={"fileId": file_id})
                    # Create new skills
                    for skill_data in cv_data["skills"]:
                        if skill_data.get("skillName"):
                            await transaction.skill.create(
                                data={
                                    "fileId": file_id,
                                    "skillName": skill_data["skillName"],
                                    "skillType": skill_data.get("skillType", "technical"),
                                    "proficiency": skill_data.get("proficiency")
                                }
                            )
                
                
                # Update certifications
                if "certifications" in cv_data:
                    # Delete existing certifications
                    await transaction.certification.delete_many(where={"fileId": file_id})
                    # Create new certifications
                    for cert_data in cv_data["certifications"]:
                        if cert_data.get("name"):
                            await transaction.certification.create(
                                data={
                                    "fileId": file_id,
                                    "name": cert_data["name"],
                                    "issuingOrganization": cert_data.get("issuingOrganization"),
                                    "issueDate": self._parse_date(cert_data.get("issueDate")),
                                    "expirationDate": self._parse_date(cert_data.get("expirationDate"))
                                }
                            )
                
                # Update projects
                if "projects" in cv_data:
                    # Delete existing projects
                    await transaction.project.delete_many(where={"fileId": file_id})
                    # Create new projects
                    for proj_data in cv_data["projects"]:
                        if proj_data.get("title"):
                            await transaction.project.create(
                                data={
                                    "fileId": file_id,
                                    "title": proj_data["title"],
                                    "description": proj_data.get("description"),
                                    "startDate": self._parse_date(proj_data.get("startDate")),
                                    "endDate": self._parse_date(proj_data.get("endDate")),
                                    "projectUrl": proj_data.get("projectUrl"),
                                    "technologies": proj_data.get("technologies", [])
                                }
                            )
                
                # Update awards and honors
                if "awardsHonors" in cv_data:
                    # Delete existing awards
                    await transaction.awardhonor.delete_many(where={"fileId": file_id})
                    # Create new awards
                    for award_data in cv_data["awardsHonors"]:
                        if award_data.get("title"):
                            await transaction.awardhonor.create(
                                data={
                                    "fileId": file_id,
                                    "title": award_data["title"],
                                    "issuingOrganization": award_data.get("issuingOrganization"),
                                    "dateReceived": self._parse_date(award_data.get("dateReceived")),
                                    "description": award_data.get("description")
                                }
                            )
                
                # Update volunteer experience
                if "volunteerExperience" in cv_data:
                    # Delete existing volunteer experience
                    await transaction.volunteerexperience.delete_many(where={"fileId": file_id})
                    # Create new volunteer experience
                    for vol_data in cv_data["volunteerExperience"]:
                        if vol_data.get("role"):
                            await transaction.volunteerexperience.create(
                                data={
                                    "fileId": file_id,
                                    "role": vol_data["role"],
                                    "organization": vol_data.get("organization"),
                                    "location": vol_data.get("location"),
                                    "startDate": self._parse_date(vol_data.get("startDate")),
                                    "endDate": self._parse_date(vol_data.get("endDate")),
                                    "description": vol_data.get("description")
                                }
                            )
                
                # Update references
                if "references" in cv_data:
                    # Delete existing references
                    await transaction.reference.delete_many(where={"fileId": file_id})
                    # Create new references
                    for ref_data in cv_data["references"]:
                        if ref_data.get("name"):
                            await transaction.reference.create(
                                data={
                                    "fileId": file_id,
                                    "name": ref_data["name"],
                                    "relationship": ref_data.get("relationship"),
                                    "email": ref_data.get("email"),
                                    "phone": ref_data.get("phone")
                                }
                            )
                
                # Update IT systems
                if "itSystems" in cv_data:
                    # Delete existing IT systems
                    await transaction.itsystem.delete_many(where={"fileId": file_id})
                    # Create new IT systems
                    for sys_data in cv_data["itSystems"]:
                        if sys_data.get("systemName"):
                            await transaction.itsystem.create(
                                data={
                                    "fileId": file_id,
                                    "systemName": sys_data["systemName"],
                                    "abbreviation": sys_data.get("abbreviation")
                                }
                            )
                
                # Update the CV file's updatedAt
                await transaction.cvfile.update(
                    where={"fileId": file_id},
                    data={"updatedAt": datetime.now()}
                )
            
            return True
        except Exception as e:
            print(f"❌ Error updating CV data: {e}")
            return False
    
    async def reset_for_retry(self, file_id: str):
        """Reset processing status for retry"""
        await self.prisma.cvfile.update(
            where={"fileId": file_id},
            data={
                "processingStatus": "pending",
                "currentStep": "Ready for retry",
                "progressPercent": 0,
                "errorMessage": None,
                "updatedAt": datetime.now()
            }
        )
    
    async def get_cv_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get CV data by file ID"""
        cv_file = await self.prisma.cvfile.find_unique(
            where={"fileId": file_id},
            include={
                "personalInfo": {
                    "include": {
                        "emails": True,
                        "phones": True,
                        "socialUrls": True
                    }
                },
                "workExperience": True,
                "education": True,
                "skills": True,
                "certifications": True,
                "projects": True,
                "awardsHonors": True,
                "volunteerExperience": True,
                "references": True,
                "itSystems": True
            }
        )
        
        if cv_file:
            return cv_file.model_dump()
        return None
    
    async def get_all_cvs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all CVs with pagination"""
        cv_files = await self.prisma.cvfile.find_many(
            take=limit,
            skip=offset,
            include={
                "personalInfo": True
            },
            order=[{"dateCreated": "desc"}]
        )
        
        return [cv_file.model_dump() for cv_file in cv_files]
    
    async def delete_cv(self, file_id: str) -> bool:
        """Delete a CV and its associated data"""
        try:
            await self.prisma.cvfile.delete(where={"fileId": file_id})
            return True
        except Exception:
            return False
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        # Get total count
        total_files = await self.prisma.cvfile.count()
        
        # Get counts by status
        completed = await self.prisma.cvfile.count(where={"processingStatus": "completed"})
        processing = await self.prisma.cvfile.count(where={"processingStatus": "processing"})
        errors = await self.prisma.cvfile.count(where={"processingStatus": "error"})
        pending = await self.prisma.cvfile.count(where={"processingStatus": "pending"})
        
        return {
            "total_files": total_files,
            "completed": completed,
            "processing": processing,
            "errors": errors,
            "pending": pending
        }
    
    # Search methods for normalized tables
    async def search_candidates(self, 
                               name: str = None,
                               skills: List[str] = None,
                               job_title: str = None,
                               company: str = None,
                               location: str = None,
                               education_degree: str = None,
                               min_experience_years: int = None,
                               certifications: List[str] = None,
                               limit: int = 50,
                               offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search candidates using normalized tables for better performance
        """
        # Build where conditions
        where_conditions = {"processingStatus": "completed"}
        
        # Add search conditions
        if name:
            where_conditions["OR"] = [
                {"personalInfo": {"firstName": {"contains": name, "mode": "insensitive"}}},
                {"personalInfo": {"lastName": {"contains": name, "mode": "insensitive"}}}
            ]
        
        if skills:
            where_conditions["skills"] = {
                "some": {
                    "skillName": {"in": skills}
                }
            }
        
        if job_title:
            where_conditions["workExperience"] = {
                "some": {
                    "jobTitle": {"contains": job_title, "mode": "insensitive"}
                }
            }
        
        if company:
            where_conditions["workExperience"] = {
                "some": {
                    "companyName": {"contains": company, "mode": "insensitive"}
                }
            }
        
        if location:
            where_conditions["OR"] = [
                {"personalInfo": {"city": {"contains": location, "mode": "insensitive"}}},
                {"personalInfo": {"state": {"contains": location, "mode": "insensitive"}}},
                {"personalInfo": {"country": {"contains": location, "mode": "insensitive"}}},
                {"workExperience": {"some": {"location": {"contains": location, "mode": "insensitive"}}}}
            ]
        
        if education_degree:
            where_conditions["education"] = {
                "some": {
                    "degree": {"contains": education_degree, "mode": "insensitive"}
                }
            }
        
        if certifications:
            where_conditions["certifications"] = {
                "some": {
                    "name": {"in": certifications}
                }
            }
        
        # Execute search
        candidates = await self.prisma.cvfile.find_many(
            where=where_conditions,
            take=limit,
            skip=offset,
            include={
                "personalInfo": True,
                "workExperience": True,
                "education": True,
                "skills": True,
                "certifications": True
            },
            order=[{"dateCreated": "desc"}]
        )
        
        return [candidate.model_dump() for candidate in candidates]
    
    async def get_candidate_details(self, file_id: str) -> Dict[str, Any]:
        """Get detailed candidate information from normalized tables"""
        cv_file = await self.prisma.cvfile.find_unique(
            where={"fileId": file_id},
            include={
                "personalInfo": True,
                "workExperience": True,
                "education": True,
                "skills": True,
                "certifications": True,
                "projects": True,
                "awardsHonors": True,
                "volunteerExperience": True,
                "references": True,
                "itSystems": True
            }
        )
        
        if not cv_file:
            return {}
        
        return cv_file.model_dump()
    
    async def get_skills_statistics(self) -> Dict[str, Any]:
        """Get statistics about skills across all candidates"""
        # Get all skills grouped by type and name
        skills_data = await self.prisma.skill.group_by(
            by=["skillType", "skillName"],
            _count={"skillName": True},
            order=[{"skillType": "asc"}, {"_count": {"skillName": "desc"}}]
        )
        
        # Organize by skill type
        technical_skills = []
        soft_skills = []
        languages = []
        
        for skill in skills_data:
            skill_info = {
                "skill_name": skill.skillName,
                "count": skill._count["skillName"]
            }
            
            if skill.skillType == "technical":
                technical_skills.append(skill_info)
            elif skill.skillType == "soft":
                soft_skills.append(skill_info)
            elif skill.skillType == "language":
                languages.append(skill_info)
        
        return {
            "technical_skills": technical_skills[:20],  # Top 20
            "soft_skills": soft_skills[:20],
            "languages": languages[:20]
        }
    
    async def verify_tables_exist(self) -> Dict[str, bool]:
        """Verify that all required tables exist"""
        try:
            # Check if tables exist by trying to count records
            cv_files_count = await self.prisma.cvfile.count()
            
            return {
                'cv_files_exists': True,
                'cv_files_count': cv_files_count
            }
        except Exception as e:
            print(f"❌ Error verifying tables: {e}")
            return {
                'cv_files_exists': False,
                'cv_files_count': 0
            }
    
    async def get_table_structure(self) -> Dict[str, Any]:
         """Get the structure of the database tables"""
         try:
             # For Prisma, we can return the schema information
             # This is a simplified version since Prisma handles schema management
             return {
                 'cv_files': [
                     {'column_name': 'id', 'data_type': 'SERIAL', 'is_nullable': 'NO'},
                     {'column_name': 'file_id', 'data_type': 'UUID', 'is_nullable': 'NO'},
                     {'column_name': 'original_filename', 'data_type': 'VARCHAR(255)', 'is_nullable': 'NO'},
                     {'column_name': 'file_type', 'data_type': 'VARCHAR(10)', 'is_nullable': 'NO'},
                     {'column_name': 'file_size', 'data_type': 'BIGINT', 'is_nullable': 'NO'},
                     {'column_name': 'file_hash', 'data_type': 'VARCHAR(64)', 'is_nullable': 'NO'},
                     {'column_name': 'converted_pdf_filename', 'data_type': 'VARCHAR(255)', 'is_nullable': 'YES'},
                     {'column_name': 'extracted_text_data', 'data_type': 'TEXT', 'is_nullable': 'YES'},
                     {'column_name': 'ai_generated_json', 'data_type': 'JSONB', 'is_nullable': 'YES'},
                     {'column_name': 'date_created', 'data_type': 'TIMESTAMPTZ', 'is_nullable': 'NO'},
                     {'column_name': 'updated_at', 'data_type': 'TIMESTAMPTz', 'is_nullable': 'NO'},
                     {'column_name': 'processing_status', 'data_type': 'VARCHAR(50)', 'is_nullable': 'NO'},
                     {'column_name': 'current_step', 'data_type': 'VARCHAR(100)', 'is_nullable': 'YES'},
                     {'column_name': 'progress_percent', 'data_type': 'INTEGER', 'is_nullable': 'NO'},
                     {'column_name': 'error_message', 'data_type': 'TEXT', 'is_nullable': 'YES'}
                 ]
             }
         except Exception as e:
             print(f"❌ Error getting table structure: {e}")
             return {'cv_files': []}

    # System Settings Methods
    async def get_settings_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all active settings for a specific category"""
        try:
            settings = await self.prisma.systemgenericsetting.find_many(
                where={
                    "category": category,
                    "isActive": True
                },
                order=[{"sortOrder": "asc"}]
            )
            # Transform camelCase to snake_case for frontend compatibility
            transformed_settings = []
            for setting in settings:
                setting_dict = setting.model_dump()
                transformed_setting = {
                    "id": setting_dict["id"],
                    "category": setting_dict["category"],
                    "setting_key": setting_dict["settingKey"],
                    "label": setting_dict["label"],
                    "value": setting_dict["value"],
                    "sort_order": setting_dict["sortOrder"],
                    "is_active": setting_dict["isActive"],
                    "created_at": setting_dict["createdAt"],
                    "updated_at": setting_dict["updatedAt"]
                }
                transformed_settings.append(transformed_setting)
            return transformed_settings
        except Exception as e:
            print(f"❌ Error fetching settings for category {category}: {e}")
            return []

    async def get_all_settings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all settings grouped by category"""
        try:
            all_settings = await self.prisma.systemgenericsetting.find_many(
                where={"isActive": True},
                order=[{"category": "asc"}, {"sortOrder": "asc"}]
            )
            
            # Group by category
            grouped_settings = {}
            for setting in all_settings:
                category = setting.category
                if category not in grouped_settings:
                    grouped_settings[category] = []
                
                # Transform camelCase to snake_case for frontend compatibility
                setting_dict = setting.model_dump()
                transformed_setting = {
                    "id": setting_dict["id"],
                    "category": setting_dict["category"],
                    "setting_key": setting_dict["settingKey"],
                    "label": setting_dict["label"],
                    "value": setting_dict["value"],
                    "sort_order": setting_dict["sortOrder"],
                    "is_active": setting_dict["isActive"],
                    "created_at": setting_dict["createdAt"],
                    "updated_at": setting_dict["updatedAt"]
                }
                grouped_settings[category].append(transformed_setting)
            
            return grouped_settings
        except Exception as e:
            print(f"❌ Error fetching all settings: {e}")
            return {}

    async def create_setting(self, setting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new setting"""
        try:
            setting = await self.prisma.systemgenericsetting.create(
                data={
                    "category": setting_data["category"],
                    "settingKey": setting_data["setting_key"],
                    "label": setting_data["label"],
                    "value": setting_data.get("value"),
                    "sortOrder": setting_data.get("sort_order", 0),
                    "isActive": setting_data.get("is_active", True)
                }
            )
            # Transform the response to snake_case for frontend compatibility
            setting_dict = setting.model_dump()
            return {
                "id": setting_dict["id"],
                "category": setting_dict["category"],
                "setting_key": setting_dict["settingKey"],
                "label": setting_dict["label"],
                "value": setting_dict["value"],
                "sort_order": setting_dict["sortOrder"],
                "is_active": setting_dict["isActive"],
                "created_at": setting_dict["createdAt"],
                "updated_at": setting_dict["updatedAt"]
            }
        except Exception as e:
            print(f"❌ Error creating setting: {e}")
            raise

    async def update_setting(self, setting_id: int, setting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing setting"""
        try:
            update_data = {}
            if "category" in setting_data:
                update_data["category"] = setting_data["category"]
            if "setting_key" in setting_data:
                update_data["settingKey"] = setting_data["setting_key"]
            if "label" in setting_data:
                update_data["label"] = setting_data["label"]
            if "value" in setting_data:
                update_data["value"] = setting_data["value"]
            if "sort_order" in setting_data:
                update_data["sortOrder"] = setting_data["sort_order"]
            if "is_active" in setting_data:
                update_data["isActive"] = setting_data["is_active"]
            
            setting = await self.prisma.systemgenericsetting.update(
                where={"id": setting_id},
                data=update_data
            )
            # Transform the response to snake_case for frontend compatibility
            setting_dict = setting.model_dump()
            return {
                "id": setting_dict["id"],
                "category": setting_dict["category"],
                "setting_key": setting_dict["settingKey"],
                "label": setting_dict["label"],
                "value": setting_dict["value"],
                "sort_order": setting_dict["sortOrder"],
                "is_active": setting_dict["isActive"],
                "created_at": setting_dict["createdAt"],
                "updated_at": setting_dict["updatedAt"]
            }
        except Exception as e:
            print(f"❌ Error updating setting: {e}")
            raise

    async def delete_setting(self, setting_id: int) -> bool:
        """Soft delete a setting by setting isActive to false"""
        try:
            print(f"🔍 Deleting setting {setting_id}...")
            
            # First, let's check what the setting looks like before deletion
            before_setting = await self.prisma.systemgenericsetting.find_unique(
                where={"id": setting_id}
            )
            print(f"🔍 Before deletion: {before_setting.model_dump() if before_setting else 'Not found'}")
            
            # Perform the soft delete
            updated_setting = await self.prisma.systemgenericsetting.update(
                where={"id": setting_id},
                data={"isActive": False}
            )
            
            print(f"🔍 After deletion: {updated_setting.model_dump()}")
            print(f"🔍 isActive is now: {updated_setting.isActive}")
            
            return True
        except Exception as e:
            print(f"❌ Error deleting setting: {e}")
            raise

    async def debug_database_state(self):
        """Debug method to check the current state of the database"""
        try:
            print(f"🔍 Debug: Checking all settings in database...")
            
            # Check database connection
            try:
                await self.prisma.connect()
                print(f"🔍 Debug: Database connected successfully")
            except Exception as e:
                print(f"❌ Debug: Database connection failed: {e}")
                return
            
            all_settings = await self.prisma.systemgenericsetting.find_many()
            print(f"🔍 Debug: Total settings in database: {len(all_settings)}")
            
            if len(all_settings) == 0:
                print(f"🔍 Debug: No settings found in database")
                return
            
            for setting in all_settings:
                print(f"   - ID: {setting.id}, Category: {setting.category}, Key: {setting.settingKey}, Label: {setting.label}, isActive: {setting.isActive}")
            
            # Check specifically for civil_status category
            civil_status_settings = await self.prisma.systemgenericsetting.find_many(
                where={"category": "civil_status"}
            )
            print(f"🔍 Debug: Civil status settings found: {len(civil_status_settings)}")
            for setting in civil_status_settings:
                print(f"   - Civil Status: ID: {setting.id}, Key: {setting.settingKey}, Label: {setting.label}, isActive: {setting.isActive}")
            
            # Check for any inactive settings
            inactive_settings = await self.prisma.systemgenericsetting.find_many(
                where={"isActive": False}
            )
            print(f"🔍 Debug: Inactive settings found: {len(inactive_settings)}")
            for setting in inactive_settings:
                print(f"   - Inactive: ID: {setting.id}, Category: {setting.category}, Key: {setting.settingKey}, Label: {setting.label}")
            
            # Check for any active settings
            active_settings = await self.prisma.systemgenericsetting.find_many(
                where={"isActive": True}
            )
            print(f"🔍 Debug: Active settings found: {len(active_settings)}")
            
            # Check database schema
            try:
                # Try to get table info
                result = await self.prisma.execute_raw("SELECT COUNT(*) as count FROM system_generic_settings")
                print(f"🔍 Debug: Raw SQL count: {result}")
                
                # Check for inactive settings using raw SQL
                inactive_result = await self.prisma.execute_raw("SELECT COUNT(*) as count FROM system_generic_settings WHERE is_active = false")
                print(f"🔍 Debug: Raw SQL inactive count: {inactive_result}")
                
                # Check for active settings using raw SQL
                active_result = await self.prisma.execute_raw("SELECT COUNT(*) as count FROM system_generic_settings WHERE is_active = true")
                print(f"🔍 Debug: Raw SQL active count: {active_result}")
                
                # Check specific records
                all_records = await self.prisma.execute_raw("SELECT id, category, setting_key, label, is_active FROM system_generic_settings ORDER BY category, setting_key LIMIT 10")
                print(f"🔍 Debug: Raw SQL sample records: {all_records}")
                
            except Exception as e:
                print(f"🔍 Debug: Raw SQL failed: {e}")
                
        except Exception as e:
            print(f"❌ Debug: Error in debug_database_state: {e}")
            import traceback
            traceback.print_exc()

    async def get_deleted_settings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all soft-deleted settings grouped by category"""
        try:
            deleted_settings = await self.prisma.systemgenericsetting.find_many(
                where={"isActive": False},
                order=[{"category": "asc"}, {"sortOrder": "asc"}]
            )
            
            if not deleted_settings or len(deleted_settings) == 0:
                return {}
            
            # Group by category
            grouped_settings = {}
            for setting in deleted_settings:
                category = setting.category
                if category not in grouped_settings:
                    grouped_settings[category] = []
                
                # Transform camelCase to snake_case for frontend compatibility
                setting_dict = setting.model_dump()
                transformed_setting = {
                    "id": setting_dict["id"],
                    "category": setting_dict["category"],
                    "setting_key": setting_dict["settingKey"],
                    "label": setting_dict["label"],
                    "value": setting_dict["value"],
                    "sort_order": setting_dict["sortOrder"],
                    "is_active": setting_dict["isActive"],
                    "created_at": setting_dict["createdAt"],
                    "updated_at": setting_dict["updatedAt"]
                }
                grouped_settings[category].append(transformed_setting)
            
            return grouped_settings
        except Exception as e:
            print(f"❌ Error fetching deleted settings: {e}")
            return {}

    async def restore_setting(self, setting_id: int) -> Dict[str, Any]:
        """Restore a soft-deleted setting by setting isActive to true"""
        try:
            setting = await self.prisma.systemgenericsetting.update(
                where={"id": setting_id},
                data={"isActive": True}
            )
            # Transform the response to snake_case for frontend compatibility
            setting_dict = setting.model_dump()
            return {
                "id": setting_dict["id"],
                "category": setting_dict["category"],
                "setting_key": setting_dict["settingKey"],
                "label": setting_dict["label"],
                "value": setting_dict["value"],
                "sort_order": setting_dict["sortOrder"],
                "is_active": setting_dict["isActive"],
                "created_at": setting_dict["createdAt"],
                "updated_at": setting_dict["updatedAt"]
            }
        except Exception as e:
            print(f"❌ Error restoring setting: {e}")
            raise

    async def permanently_delete_setting(self, setting_id: int) -> bool:
        """Permanently delete a setting from the database"""
        try:
            await self.prisma.systemgenericsetting.delete(
                where={"id": setting_id}
            )
            return True
        except Exception as e:
            print(f"❌ Error permanently deleting setting: {e}")
            raise

    async def save_ai_output(self, file_id: str, ai_output: Dict[str, Any]) -> bool:
        """Save AI-generated output to the database"""
        try:
            # Update the CV file with AI output
            await self.prisma.cvfile.update(
                where={"fileId": file_id},
                data={
                    "aiGeneratedJson": ai_output,
                    "processingStatus": "completed",
                    "currentStep": "AI processing completed",
                    "progressPercent": 100,
                    "updatedAt": datetime.utcnow()
                }
            )
            
            print(f"✅ AI output saved successfully for file {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save AI output: {e}")
            return False

    async def save_text_lines(self, file_id: str, text_lines: List[Dict[str, Any]]) -> bool:
        """
        Save individual text lines to database for full-text search
        """
        try:
            # Delete existing text lines for this file
            await self.prisma.cvtextline.delete_many(
                where={"fileId": file_id}
            )
            
            # Insert new text lines
            for line_data in text_lines:
                await self.prisma.cvtextline.create(data=line_data)
            
            print(f"✅ Saved {len(text_lines)} text lines for file {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save text lines: {e}")
            return False

    async def search_cv_text(self, search_query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Perform full-text search across all CV text lines and extracted text data
        """
        try:
            results = []
            
            # First, try full-text search in cv_text_lines table
            try:
                text_line_results = await self.prisma.query_raw(
                    """
                    SELECT 
                        ctl.file_id,
                        ctl.line_number,
                        ctl.line_text,
                        ctl.line_type,
                        cf.original_filename,
                        ts_rank(to_tsvector('english', ctl.line_text), plainto_tsquery('english', $1)) as rank
                    FROM cv_text_lines ctl
                    JOIN cv_files cf ON ctl.file_id = cf.file_id
                    WHERE to_tsvector('english', ctl.line_text) @@ plainto_tsquery('english', $1)
                    ORDER BY rank DESC, ctl.file_id, ctl.line_number
                    LIMIT $2
                    """,
                    search_query, limit
                )
                results.extend(text_line_results)
                print(f"🔍 Full-text search found {len(text_line_results)} results in cv_text_lines")
            except Exception as e:
                print(f"⚠️ Full-text search in cv_text_lines failed: {e}")
            
            # If we don't have enough results, fall back to searching extractedTextData
            if len(results) < limit:
                remaining_limit = limit - len(results)
                try:
                    fallback_results = await self.prisma.query_raw(
                        """
                        SELECT 
                            cf.file_id,
                            0 as line_number,
                            cf.extracted_text_data as line_text,
                            'extracted_text' as line_type,
                            cf.original_filename,
                            0.5 as rank
                        FROM cv_files cf
                        WHERE cf.extracted_text_data IS NOT NULL 
                        AND cf.extracted_text_data ILIKE $1
                        AND cf.processing_status = 'completed'
                        ORDER BY cf.date_created DESC
                        LIMIT $2
                        """,
                        f'%{search_query}%', remaining_limit
                    )
                    results.extend(fallback_results)
                    print(f"🔍 Fallback search found {len(fallback_results)} results in extractedTextData")
                except Exception as e:
                    print(f"⚠️ Fallback search failed: {e}")
            
            # Remove duplicates and limit results
            unique_results = []
            seen_file_ids = set()
            for result in results:
                if result['file_id'] not in seen_file_ids:
                    unique_results.append(result)
                    seen_file_ids.add(result['file_id'])
                    if len(unique_results) >= limit:
                        break
            
            return unique_results[:limit]
            
        except Exception as e:
            print(f"❌ Full-text search failed: {e}")
            return []

    async def search_cv_text_partial(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Perform partial text search using trigram matching with fallback
        """
        try:
            results = []
            
            # First, try trigram search in cv_text_lines table
            try:
                text_line_results = await self.prisma.query_raw(
                    """
                    SELECT 
                        ctl.file_id,
                        ctl.line_number,
                        ctl.line_text,
                        ctl.line_type,
                        cf.original_filename,
                        similarity(ctl.line_text, $1) as similarity_score
                    FROM cv_text_lines ctl
                    JOIN cv_files cf ON ctl.file_id = cf.file_id
                    WHERE ctl.line_text % $1
                    ORDER BY similarity_score DESC, ctl.file_id, ctl.line_number
                    LIMIT $2
                    """,
                    search_term, limit
                )
                results.extend(text_line_results)
                print(f"🔍 Partial search found {len(text_line_results)} results in cv_text_lines")
            except Exception as e:
                print(f"⚠️ Partial search in cv_text_lines failed: {e}")
            
            # If we don't have enough results, fall back to searching extractedTextData
            if len(results) < limit:
                remaining_limit = limit - len(results)
                try:
                    fallback_results = await self.prisma.query_raw(
                        """
                        SELECT 
                            cf.file_id,
                            0 as line_number,
                            cf.extracted_text_data as line_text,
                            'extracted_text' as line_type,
                            cf.original_filename,
                            0.5 as similarity_score
                        FROM cv_files cf
                        WHERE cf.extracted_text_data IS NOT NULL 
                        AND cf.extracted_text_data ILIKE $1
                        AND cf.processing_status = 'completed'
                        ORDER BY cf.date_created DESC
                        LIMIT $2
                        """,
                        f'%{search_term}%', remaining_limit
                    )
                    results.extend(fallback_results)
                    print(f"🔍 Fallback partial search found {len(fallback_results)} results in extractedTextData")
                except Exception as e:
                    print(f"⚠️ Fallback partial search failed: {e}")
            
            # Remove duplicates and limit results
            unique_results = []
            seen_file_ids = set()
            for result in results:
                if result['file_id'] not in seen_file_ids:
                    unique_results.append(result)
                    seen_file_ids.add(result['file_id'])
                    if len(unique_results) >= limit:
                        break
            
            return unique_results[:limit]
            
        except Exception as e:
            print(f"❌ Partial text search failed: {e}")
            return []

    async def get_cv_context(self, file_id: str, line_number: int, context_lines: int = 3) -> Dict[str, Any]:
        """
        Get context around a specific text line
        """
        try:
            # Get the target line and surrounding context
            context_results = await self.prisma.query_raw(
                """
                SELECT 
                    line_number,
                    line_text,
                    line_type
                FROM cv_text_lines
                WHERE file_id = $1 
                AND line_number BETWEEN $2 - $3 AND $2 + $3
                ORDER BY line_number
                """,
                file_id, line_number, context_lines
            )
            
            return {
                'file_id': file_id,
                'target_line': line_number,
                'context_lines': context_results
            }
            
        except Exception as e:
            print(f"❌ Failed to get CV context: {e}")
            return {}

    async def get_cv_text_lines(self, file_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all text lines for a specific CV file
        """
        try:
            text_lines = await self.prisma.cvtextline.find_many(
                where={"fileId": file_id},
                order={"lineNumber": "asc"},
                take=limit
            )
            
            return [line.model_dump() for line in text_lines]
            
        except Exception as e:
            print(f"❌ Failed to get CV text lines: {e}")
            return []

    async def search_cvs_combined(self, 
                                  search_query: str = None,
                                  status_filter: str = None,
                                  file_type_filter: str = None,
                                  limit: int = 50,
                                  offset: int = 0) -> Dict[str, Any]:
        """
        Search CVs using both structured data and full-text search across cv_text_lines
        This provides comprehensive search capabilities including content within documents
        """
        try:
            # If no search query, just filter by status and file type
            if not search_query or not search_query.strip():
                where_conditions = {}
                
                # Add status filter
                if status_filter and status_filter != "all":
                    where_conditions["processingStatus"] = status_filter
                
                # Add file type filter
                if file_type_filter and file_type_filter != "all":
                    where_conditions["fileType"] = file_type_filter
                
                # Get total count for pagination
                total_count = await self.prisma.cvfile.count(where=where_conditions)
                
                # Get CVs with pagination and includes
                cv_files = await self.prisma.cvfile.find_many(
                    where=where_conditions,
                    take=limit,
                    skip=offset,
                    include={
                        "personalInfo": {
                            "include": {
                                "emails": True,
                                "phones": True,
                                "socialUrls": True
                            }
                        },
                        "workExperience": True,
                        "education": True,
                        "skills": True
                    },
                    order=[{"dateCreated": "desc"}]
                )
                
                return {
                    "cv_files": [cv_file.model_dump() for cv_file in cv_files],
                    "total_count": total_count,
                    "search_method": "filter_only"
                }
            
            # If there's a search query, use combined search approach
            print(f"🔍 Performing combined search for: '{search_query}'")
            
            # Step 1: Search in cv_text_lines table for full-text matches
            text_search_results = await self.prisma.query_raw("""
                SELECT DISTINCT 
                    ctl.file_id,
                    cf.id as cv_id,
                    cf.original_filename,
                    cf.processing_status,
                    cf.file_type,
                    cf.date_created,
                    cf.updated_at,
                    ts_rank(to_tsvector('english', ctl.line_text), plainto_tsquery('english', $1)) as rank
                FROM cv_text_lines ctl
                JOIN cv_files cf ON ctl.file_id = cf.file_id
                WHERE to_tsvector('english', ctl.line_text) @@ plainto_tsquery('english', $1)
                ORDER BY rank DESC
                LIMIT $2
            """, search_query, limit * 2)  # Get more results to account for filtering
            
            # Step 2: Search in structured fields using Prisma
            structured_where_conditions = {"processingStatus": "completed"}
            
            # Add status filter
            if status_filter and status_filter != "all":
                structured_where_conditions["processingStatus"] = status_filter
            
            # Add file type filter
            if file_type_filter and file_type_filter != "all":
                structured_where_conditions["fileType"] = file_type_filter
            
            # Add structured search conditions
            structured_where_conditions["OR"] = [
                {"originalFilename": {"contains": search_query, "mode": "insensitive"}},
                {"personalInfo": {"firstName": {"contains": search_query, "mode": "insensitive"}}},
                {"personalInfo": {"lastName": {"contains": search_query, "mode": "insensitive"}}},
                {"personalInfo": {"emails": {"some": {"email": {"contains": search_query, "mode": "insensitive"}}}}},
                {"extractedTextData": {"contains": search_query, "mode": "insensitive"}}
            ]
            
            structured_results = await self.prisma.cvfile.find_many(
                where=structured_where_conditions,
                take=limit,
                skip=0,  # Don't skip for structured search
                include={
                    "personalInfo": {
                        "include": {
                            "emails": True,
                            "phones": True,
                            "socialUrls": True
                        }
                    },
                    "workExperience": True,
                    "education": True,
                    "skills": True
                },
                order=[{"dateCreated": "desc"}]
            )
            
            # Step 3: Combine and deduplicate results
            combined_file_ids = set()
            combined_results = []
            
            # Add text search results first (they have relevance ranking)
            for text_result in text_search_results:
                file_id = text_result['file_id']
                if file_id not in combined_file_ids:
                    combined_file_ids.add(file_id)
                    
                    # Get full CV data for this file_id
                    cv_data = await self.prisma.cvfile.find_unique(
                        where={"fileId": file_id},
                        include={
                            "personalInfo": {
                                "include": {
                                    "emails": True,
                                    "phones": True,
                                    "socialUrls": True
                                }
                            },
                            "workExperience": True,
                            "education": True,
                            "skills": True
                        }
                    )
                    
                    if cv_data:
                        # Apply status and file type filters
                        if status_filter and status_filter != "all" and cv_data.processingStatus != status_filter:
                            continue
                        if file_type_filter and file_type_filter != "all" and cv_data.fileType != file_type_filter:
                            continue
                        
                        combined_results.append(cv_data.model_dump())
                        if len(combined_results) >= limit:
                            break
            
            # Add structured search results if we haven't reached the limit
            for structured_result in structured_results:
                file_id = structured_result.fileId
                if file_id not in combined_file_ids and len(combined_results) < limit:
                    combined_file_ids.add(file_id)
                    combined_results.append(structured_result.model_dump())
            
            # Get total count for pagination (this is approximate for combined search)
            total_count = len(combined_results)
            if len(combined_results) < limit:
                # If we have fewer results than limit, get more from database
                remaining_limit = limit - len(combined_results)
                additional_results = await self.prisma.cvfile.find_many(
                    where={"processingStatus": "completed"},
                    take=remaining_limit,
                    skip=0,
                    include={
                        "personalInfo": {
                            "include": {
                                "emails": True,
                                "phones": True,
                                "socialUrls": True
                            }
                        },
                        "workExperience": True,
                        "education": True,
                        "skills": True
                    },
                    order=[{"dateCreated": "desc"}]
                )
                
                for result in additional_results:
                    if result.fileId not in combined_file_ids and len(combined_results) < limit:
                        combined_file_ids.add(result.fileId)
                        combined_results.append(result.model_dump())
            
            return {
                "cv_files": combined_results,
                "total_count": total_count,
                "search_method": "combined_search",
                "text_search_results": len([r for r in text_search_results if r['file_id'] in combined_file_ids]),
                "structured_search_results": len([r for r in structured_results if r.fileId in combined_file_ids])
            }
            
        except Exception as e:
            print(f"❌ Combined search failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "cv_files": [],
                "total_count": 0,
                "search_method": "error",
                "error": str(e)
            }
