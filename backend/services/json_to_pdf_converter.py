import json
import asyncio
from pathlib import Path
from typing import Dict, Any
import aiofiles

class JSONToPDFConverter:
    """
    Service to convert JSON CV data to formatted PDF documents
    """
    
    async def convert_json_to_pdf(self, json_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Convert JSON CV data to a formatted PDF document
        """
        try:
            # Debug: Print the structure of the JSON data
            print(f"🔍 JSON to PDF conversion - Data structure:")
            print(f"   Type: {type(json_data)}")
            print(f"   Keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            
            # Validate that json_data is a dictionary
            if not isinstance(json_data, dict):
                raise Exception(f"Expected dictionary for json_data, got {type(json_data).__name__}")
            
            # Validate and sanitize the JSON structure
            json_data = self._sanitize_json_structure(json_data)
            
            # Import reportlab for PDF generation
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            section_style = ParagraphStyle(
                'CustomSection',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Add title
            if 'personal_information' in json_data:
                personal_info = json_data['personal_information']
                full_name = f"{personal_info.get('first_name', '')} {personal_info.get('last_name', '')}".strip()
                if full_name:
                    story.append(Paragraph(f"Curriculum Vitae - {full_name}", title_style))
                else:
                    story.append(Paragraph("Curriculum Vitae", title_style))
            else:
                story.append(Paragraph("Curriculum Vitae", title_style))
            
            story.append(Spacer(1, 12))
            
            # Personal Information Section
            if 'personal_information' in json_data:
                story.append(Paragraph("Personal Information", section_style))
                personal_info = json_data['personal_information']
                
                if not isinstance(personal_info, dict):
                    personal_info = {}
                
                # Create personal info table
                personal_data = []
                if personal_info.get('first_name') or personal_info.get('last_name'):
                    # Safely get name components, converting None to empty string
                    first_name = personal_info.get('first_name') or ''
                    middle_name = personal_info.get('middle_name') or ''
                    last_name = personal_info.get('last_name') or ''
                    
                    name_parts = [part for part in [first_name, middle_name, last_name] if part]
                    full_name = ' '.join(name_parts)
                    personal_data.append(['Name:', full_name])
                
                if personal_info.get('emails'):
                    emails = personal_info['emails']
                    print(f"🔍 Emails data: {emails} (type: {type(emails)})")
                    
                    # Handle different email data structures
                    if isinstance(emails, list):
                        email_text = ', '.join([str(email) for email in emails if email])
                    elif isinstance(emails, str):
                        email_text = emails
                    else:
                        print(f"⚠️  Unexpected emails format: {emails} (type: {type(emails)})")
                        email_text = str(emails)
                    
                    if email_text:
                        personal_data.append(['Email:', email_text])
                
                if personal_info.get('phones'):
                    phones = personal_info['phones']
                    print(f"🔍 Phones data: {phones} (type: {type(phones)})")
                    
                    # Handle different phone data structures
                    if isinstance(phones, list):
                        phone_texts = []
                        for phone in phones:
                            if isinstance(phone, dict):
                                # Safely get phone components, converting None to empty string
                                phone_type = phone.get('type') or ''
                                phone_number = phone.get('number') or ''
                                phone_text = f"{phone_type}: {phone_number}" if phone_type and phone_number else phone_type or phone_number
                                phone_texts.append(phone_text)
                            elif isinstance(phone, str):
                                phone_texts.append(phone)
                            else:
                                print(f"⚠️  Unexpected phone format: {phone} (type: {type(phone)})")
                                phone_texts.append(str(phone))
                        phone_text = ', '.join(phone_texts)
                    elif isinstance(phones, str):
                        phone_text = phones
                    else:
                        print(f"⚠️  Unexpected phones format: {phones} (type: {type(phones)})")
                        phone_text = str(phones)
                    
                    if phone_text:
                        personal_data.append(['Phone:', phone_text])
                
                if personal_info.get('address'):
                    addr = personal_info['address']
                    print(f"🔍 Address data: {addr} (type: {type(addr)})")
                    
                    # Handle different address data structures
                    if isinstance(addr, dict):
                        # Safely get address components, converting None to empty string
                        street = addr.get('street') or ''
                        barangay = addr.get('barangay') or ''
                        city = addr.get('city') or ''
                        state = addr.get('state') or ''
                        postal_code = addr.get('postal_code') or ''
                        country = addr.get('country') or ''
                        
                        address_parts = [part for part in [street, barangay, city, state, postal_code, country] if part]
                        address_text = ', '.join(address_parts)
                    elif isinstance(addr, str):
                        address_text = addr
                    else:
                        print(f"⚠️  Unexpected address format: {addr} (type: {type(addr)})")
                        address_text = str(addr)
                    
                    if address_text:
                        personal_data.append(['Address:', address_text])
                
                if personal_data:
                    personal_table = Table(personal_data, colWidths=[1.5*inch, 4*inch])
                    personal_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                    ]))
                    story.append(personal_table)
                
                story.append(Spacer(1, 12))
            
            # Professional Summary
            if json_data.get('professional_summary'):
                story.append(Paragraph("Professional Summary", section_style))
                story.append(Paragraph(json_data['professional_summary'], normal_style))
                story.append(Spacer(1, 12))
            
            # Work Experience
            if json_data.get('work_experience') and len(json_data['work_experience']) > 0:
                story.append(Paragraph("Work Experience", section_style))
                
                for i, experience in enumerate(json_data['work_experience']):
                    if not isinstance(experience, dict):
                        continue
                        
                    job_title = experience.get('job_title', '')
                    company = experience.get('company_name', '')
                    location = experience.get('location', '')
                    start_date = experience.get('start_date', '')
                    end_date = experience.get('end_date', '')
                    
                    # Job header
                    job_header = f"{job_title}"
                    if company:
                        job_header += f" at {company}"
                    if location:
                        job_header += f" ({location})"
                    
                    story.append(Paragraph(job_header, ParagraphStyle(
                        'JobHeader',
                        parent=styles['Heading3'],
                        fontSize=12,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    
                    # Job period
                    if start_date or end_date:
                        # Safely handle date formatting, converting None to empty string
                        start_str = start_date or ''
                        end_str = end_date or ''
                        if start_str and end_str:
                            period_text = f"{start_str} - {end_str}"
                        else:
                            period_text = start_str or end_str
                        story.append(Paragraph(period_text, ParagraphStyle(
                            'JobPeriod',
                            parent=styles['Normal'],
                            fontSize=9,
                            spaceAfter=6,
                            textColor=colors.grey
                        )))
                    
                    # Job responsibilities
                    responsibilities = experience.get('responsibilities')
                    if responsibilities and isinstance(responsibilities, list) and responsibilities:
                        for responsibility in responsibilities:
                            if responsibility:
                                story.append(Paragraph(f"• {responsibility}", normal_style))
                    
                    if i < len(json_data['work_experience']) - 1:
                        story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
            
            # Education
            if json_data.get('education') and len(json_data['education']) > 0:
                story.append(Paragraph("Education", section_style))
                
                for i, education in enumerate(json_data['education']):
                    if not isinstance(education, dict):
                        continue
                        
                    degree = education.get('degree', '')
                    institution = education.get('institution', '')
                    location = education.get('location', '')
                    start_date = education.get('start_date', '')
                    end_date = education.get('end_date', '')
                    gpa = education.get('gpa', '')
                    honors = education.get('honors', '')
                    
                    # Education header
                    edu_header = degree
                    if institution:
                        edu_header += f" - {institution}"
                    if location:
                        edu_header += f" ({location})"
                    
                    story.append(Paragraph(edu_header, ParagraphStyle(
                        'EduHeader',
                        parent=styles['Heading3'],
                        fontSize=12,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    
                    # Education period and details
                    details = []
                    if start_date or end_date:
                        # Safely handle date formatting, converting None to empty string
                        start_str = start_date or ''
                        end_str = end_date or ''
                        if start_str and end_str:
                            period_text = f"{start_str} - {end_str}"
                        else:
                            period_text = start_str or end_str
                        details.append(period_text)
                    if gpa:
                        details.append(f"GPA: {gpa}")
                    if honors:
                        details.append(f"Honors: {honors}")
                    
                    if details:
                        story.append(Paragraph(', '.join(details), ParagraphStyle(
                            'EduDetails',
                            parent=styles['Normal'],
                            fontSize=9,
                            spaceAfter=6,
                            textColor=colors.grey
                        )))
                    
                    if i < len(json_data['education']) - 1:
                        story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
            
            # Skills
            if json_data.get('skills'):
                story.append(Paragraph("Skills", section_style))
                skills = json_data['skills']
                
                if skills and isinstance(skills, dict) and skills.get('technical_skills'):
                    story.append(Paragraph("Technical Skills:", ParagraphStyle(
                        'SkillCategory',
                        parent=styles['Heading4'],
                        fontSize=11,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    tech_skills = skills['technical_skills']
                    if isinstance(tech_skills, list) and tech_skills:
                        tech_skills_text = ', '.join([str(skill) for skill in tech_skills if skill])
                        story.append(Paragraph(tech_skills_text, normal_style))
                        story.append(Spacer(1, 6))
                
                if skills and isinstance(skills, dict) and skills.get('soft_skills'):
                    story.append(Paragraph("Soft Skills:", ParagraphStyle(
                        'SkillCategory',
                        parent=styles['Heading4'],
                        fontSize=11,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    soft_skills = skills['soft_skills']
                    if isinstance(soft_skills, list) and soft_skills:
                        soft_skills_text = ', '.join([str(skill) for skill in soft_skills if skill])
                        story.append(Paragraph(soft_skills_text, normal_style))
                        story.append(Spacer(1, 6))
                
                if skills and isinstance(skills, dict) and skills.get('computer_languages'):
                    story.append(Paragraph("Computer Languages:", ParagraphStyle(
                        'SkillCategory',
                        parent=styles['Heading4'],
                        fontSize=11,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    computer_languages = skills['computer_languages']
                    if isinstance(computer_languages, list) and computer_languages:
                        for lang in computer_languages:
                            if isinstance(lang, dict):
                                # Safely get language components, converting None to empty string
                                language = lang.get('language') or ''
                                proficiency = lang.get('proficiency') or ''
                                if language and proficiency:
                                    lang_text = f"{language} ({proficiency})"
                                else:
                                    lang_text = language or proficiency
                                if lang_text:
                                    story.append(Paragraph(lang_text, normal_style))
                
                story.append(Spacer(1, 12))
            
            # Projects
            if json_data.get('projects') and len(json_data['projects']) > 0:
                story.append(Paragraph("Projects", section_style))
                
                for i, project in enumerate(json_data['projects']):
                    if not isinstance(project, dict):
                        continue
                        
                    title = project.get('title', '')
                    description = project.get('description', '')
                    technologies = project.get('technologies_used', [])
                    start_date = project.get('start_date', '')
                    end_date = project.get('end_date', '')
                    
                    # Project header
                    project_header = title
                    if start_date or end_date:
                        # Safely handle date formatting, converting None to empty string
                        start_str = start_date or ''
                        end_str = end_date or ''
                        if start_str and end_str:
                            period_text = f"{start_str} - {end_str}"
                        else:
                            period_text = start_str or end_str
                        project_header += f" ({period_text})"
                    
                    story.append(Paragraph(project_header, ParagraphStyle(
                        'ProjectHeader',
                        parent=styles['Heading3'],
                        fontSize=12,
                        spaceAfter=4,
                        textColor=colors.darkblue
                    )))
                    
                    # Project description
                    if description:
                        story.append(Paragraph(description, normal_style))
                    
                    # Project technologies
                    if technologies and isinstance(technologies, list) and technologies:
                        tech_text = f"Technologies: {', '.join([str(tech) for tech in technologies if tech])}"
                        story.append(Paragraph(tech_text, ParagraphStyle(
                            'ProjectTech',
                            parent=styles['Normal'],
                            fontSize=9,
                            spaceAfter=6,
                            textColor=colors.grey
                        )))
                    
                    if i < len(json_data['projects']) - 1:
                        story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
            
            # Certifications
            if json_data.get('certifications') and len(json_data['certifications']) > 0:
                story.append(Paragraph("Certifications", section_style))
                
                for i, cert in enumerate(json_data['certifications']):
                    if not isinstance(cert, dict):
                        continue
                        
                    name = cert.get('name', '')
                    organization = cert.get('issuing_organization', '')
                    issue_date = cert.get('issue_date', '')
                    expiration_date = cert.get('expiration_date', '')
                    
                    cert_text = name
                    if organization:
                        cert_text += f" - {organization}"
                    if issue_date:
                        cert_text += f" (Issued: {issue_date}"
                        if expiration_date:
                            cert_text += f", Expires: {expiration_date}"
                        cert_text += ")"
                    
                    story.append(Paragraph(cert_text, normal_style))
                    
                    if i < len(json_data['certifications']) - 1:
                        story.append(Spacer(1, 4))
                
                story.append(Spacer(1, 12))
            
            # References
            if json_data.get('references') and len(json_data['references']) > 0:
                story.append(Paragraph("References", section_style))
                
                for i, ref in enumerate(json_data['references']):
                    if not isinstance(ref, dict):
                        continue
                        
                    name = ref.get('name', '')
                    relationship = ref.get('relationship', '')
                    email = ref.get('email', '')
                    phone = ref.get('phone', '')
                    
                    ref_text = name
                    if relationship:
                        ref_text += f" - {relationship}"
                    if email:
                        ref_text += f" ({email})"
                    if phone:
                        ref_text += f" - {phone}"
                    
                    story.append(Paragraph(ref_text, normal_style))
                    
                    if i < len(json_data['references']) - 1:
                        story.append(Spacer(1, 4))
            
            # Build PDF
            doc.build(story)
            
            if output_path.exists():
                return output_path
            else:
                raise Exception("PDF generation failed - file not created")
                
        except ImportError:
            raise Exception("reportlab not installed. Please install it with: pip install reportlab")
        except Exception as e:
            raise Exception(f"JSON to PDF conversion failed: {str(e)}")

    def _sanitize_json_structure(self, data: Any) -> Any:
        """
        Sanitize and normalize JSON structure to handle unexpected data types
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized[key] = self._sanitize_json_structure(value)
            return sanitized
        elif isinstance(data, list):
            sanitized = []
            for item in data:
                sanitized.append(self._sanitize_json_structure(item))
            return sanitized
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        else:
            print(f"⚠️  Converting unexpected type {type(data)} to string: {data}")
            return str(data)

