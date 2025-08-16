import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { ArrowLeft, FileText, FileJson, Download, Eye, User, Briefcase, GraduationCap, Award, FileCheck, Users, Star, Mail, Phone, MapPin, Calendar, FileDown } from 'lucide-react';
import { useState, useEffect, type FC } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';

interface CVFile {
  id: string;
  fileId: string;
  originalFilename: string;
  fileType: string;
  fileSize: number;
  processingStatus: string;
  currentStep: string;
  progressPercent: number;
  dateCreated: string;
  dateModified: string;
  convertedPdfFilename?: string;
  aiGeneratedJson?: any; // AI generated JSON from database
  aiOutput?: any; // Legacy field
  personalInfo?: {
    firstName?: string;
    lastName?: string;
    emails?: Array<{ email: string; emailType?: string }>;
    phones?: Array<{ phone: string; phoneType?: string }>;
    city?: string;
    state?: string;
    country?: string;
  };
  workExperience?: Array<{
    jobTitle?: string;
    companyName?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
  }>;
  education?: Array<{
    degree?: string;
    institution?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
  }>;
  skills?: Array<{
    skillName: string;
    skillType: string;
    proficiency?: string;
  }>;
}

// Component to render structured JSON data
const StructuredJSONViewer: FC<{ data: any }> = ({ data }) => {
  if (!data) return null;

  const renderPersonalInfo = (personalInfo: any) => {
    if (!personalInfo) return null;
    
    return (
             <div className="space-y-4">
         <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-user">👤</span>
           Personal Information
         </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Name Fields */}
          {personalInfo.first_name && (
            <div>
              <p className="font-medium text-sm text-gray-600">First Name</p>
              <p className="text-sm">{personalInfo.first_name}</p>
            </div>
          )}
          {personalInfo.last_name && (
            <div>
              <p className="font-medium text-sm text-gray-600">Last Name</p>
              <p className="text-sm">{personalInfo.last_name}</p>
            </div>
          )}
          {personalInfo.middle_name && (
            <div>
              <p className="font-medium text-sm text-gray-600">Middle Name</p>
              <p className="text-sm">{personalInfo.middle_name}</p>
            </div>
          )}
          {personalInfo.birth_date && (
            <div>
              <p className="font-medium text-sm text-gray-600">Birth Date</p>
              <p className="text-sm">{personalInfo.birth_date}</p>
            </div>
          )}
          {personalInfo.gender && (
            <div>
              <p className="font-medium text-sm text-gray-600">Gender</p>
              <p className="text-sm">{personalInfo.gender}</p>
            </div>
          )}
          {personalInfo.civil_status && (
            <div>
              <p className="font-medium text-sm text-gray-600">Civil Status</p>
              <p className="text-sm">{personalInfo.civil_status}</p>
            </div>
          )}
          
          {/* Contact Information */}
          {personalInfo.emails && personalInfo.emails.length > 0 && (
            <div className="md:col-span-2">
                                              <p className="font-medium text-sm text-gray-600 flex items-center gap-1">
                   <span className="icon icon-mail">📧</span>
                   Emails
                 </p>
              <div className="space-y-1">
                {personalInfo.emails.map((email: string, index: number) => (
                  <p key={index} className="text-sm">{email}</p>
                ))}
              </div>
            </div>
          )}
          {personalInfo.phones && personalInfo.phones.length > 0 && (
            <div className="md:col-span-2">
                                              <p className="font-medium text-sm text-gray-600 flex items-center gap-1">
                   <span className="icon icon-phone">📞</span>
                   Phone Numbers
                 </p>
              <div className="space-y-1">
                {personalInfo.phones.map((phone: any, index: number) => (
                  <p key={index} className="text-sm">
                    {phone.type}: {phone.number}
                  </p>
                ))}
              </div>
            </div>
          )}
          
          {/* Additional Personal Info */}
          {personalInfo.alias && personalInfo.alias.length > 0 && (
            <div className="md:col-span-2">
              <p className="font-medium text-sm text-gray-600">Aliases</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {personalInfo.alias.map((alias: string, index: number) => (
                  <span key={index} className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                    {alias}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Work Preferences */}
          {personalInfo.work_preference && (
            <div className="md:col-span-2">
              <p className="font-medium text-sm text-gray-600">Work Preferences</p>
              <div className="flex gap-4 mt-1">
                <span className="text-sm">
                  Remote: {personalInfo.work_preference.open_to_work_from_home ? 'Yes' : 'No'}
                </span>
                <span className="text-sm">
                  On-site: {personalInfo.work_preference.open_to_onsite ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          )}
          
          {/* Social URLs */}
          {personalInfo.social_urls && personalInfo.social_urls.length > 0 && (
            <div className="md:col-span-2">
              <p className="font-medium text-sm text-gray-600">Social Media</p>
              <div className="space-y-1">
                {personalInfo.social_urls.map((social: any, index: number) => (
                  <p key={index} className="text-sm">
                    {social.platform}: <a href={social.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{social.url}</a>
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderAddress = (address: any) => {
    if (!address) return null;
    
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <span className="icon icon-map-pin">📍</span>
          Address
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {address.street && (
            <div className="md:col-span-2">
              <p className="font-medium text-sm text-gray-600">Street Address</p>
              <p className="text-sm">{address.street}</p>
            </div>
          )}
          {address.barangay && (
            <div>
              <p className="font-medium text-sm text-gray-600">Barangay</p>
              <p className="text-sm">{address.barangay}</p>
            </div>
          )}
          {address.city && (
            <div>
              <p className="font-medium text-sm text-gray-600">City</p>
              <p className="text-sm">{address.city}</p>
            </div>
          )}
          {address.state && (
            <div>
              <p className="font-medium text-sm text-gray-600">State/Province</p>
              <p className="text-sm">{address.state}</p>
            </div>
          )}
          {address.postal_code && (
            <div>
              <p className="font-medium text-sm text-gray-600">Postal Code</p>
              <p className="text-sm">{address.postal_code}</p>
            </div>
          )}
          {address.country && (
            <div>
              <p className="font-medium text-sm text-gray-600">Country</p>
              <p className="text-sm">{address.country}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderWorkExperience = (workExp: any[]) => {
    if (!workExp || workExp.length === 0) return null;
    
    return (
      <div className="space-y-4">
                 <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-briefcase">💼</span>
           Work Experience
         </h3>
        <div className="space-y-4">
          {workExp.map((job, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-sm">{job.job_title}</p>
                  <p className="text-sm text-gray-600">{job.company_name}</p>
                  <p className="text-sm text-gray-500">{job.location}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    {job.start_date} - {job.end_date}
                  </p>
                </div>
              </div>
              {job.responsibilities && job.responsibilities.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-600">Responsibilities:</p>
                  <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
                    {job.responsibilities.map((resp: string, respIndex: number) => (
                      <li key={respIndex}>{resp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderEducation = (education: any[]) => {
    if (!education || education.length === 0) return null;
    
    return (
      <div className="space-y-4">
                 <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-graduation">🎓</span>
           Education
         </h3>
        <div className="space-y-4">
          {education.map((edu, index) => (
            <div key={index} className="border-l-4 border-green-500 pl-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-sm">{edu.degree}</p>
                  <p className="text-sm text-gray-600">{edu.institution}</p>
                  <p className="text-sm text-gray-500">{edu.location}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    {edu.start_date} - {edu.end_date}
                  </p>
                </div>
              </div>
              {edu.gpa && (
                <p className="text-sm text-gray-600 mt-1">GPA: {edu.gpa}</p>
              )}
              {edu.honors && (
                <p className="text-sm text-gray-600">Honors: {edu.honors}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSkills = (skills: any) => {
    if (!skills) return null;
    
    return (
      <div className="space-y-4">
                 <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-star">⭐</span>
           Skills
         </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {skills.technical_skills && skills.technical_skills.length > 0 && (
            <div>
              <p className="font-medium text-sm text-gray-600">Technical Skills</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {skills.technical_skills.map((skill: string, index: number) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {skills.soft_skills && skills.soft_skills.length > 0 && (
            <div>
              <p className="font-medium text-sm text-gray-600">Soft Skills</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {skills.soft_skills.map((skill: string, index: number) => (
                  <span key={index} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {skills.computer_languages && skills.computer_languages.length > 0 && (
            <div className="md:col-span-2">
              <p className="font-medium text-sm text-gray-600">Programming Languages</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {skills.computer_languages.map((lang: any, index: number) => (
                  <span key={index} className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                    {lang.language} ({lang.proficiency})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderCertifications = (certs: any[]) => {
    if (!certs || certs.length === 0) return null;
    
    return (
      <div className="space-y-4">
                                            <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-file-check">📋</span>
           Certifications
         </h3>
        <div className="space-y-3">
          {certs.map((cert, index) => (
            <div key={index} className="border-l-4 border-yellow-500 pl-4">
              <p className="font-semibold text-sm">{cert.name}</p>
              <p className="text-sm text-gray-600">{cert.issuing_organization}</p>
              <p className="text-sm text-gray-500">
                {cert.issue_date} - {cert.expiration_date || 'No Expiration'}
              </p>
              {cert.credential_id && (
                <p className="text-sm text-gray-500">ID: {cert.credential_id}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderProjects = (projects: any[]) => {
    if (!projects || projects.length === 0) return null;
    
    return (
      <div className="space-y-4">
                 <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-star">⭐</span>
           Projects
         </h3>
        <div className="space-y-4">
          {projects.map((project, index) => (
            <div key={index} className="border-l-4 border-indigo-500 pl-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-sm">{project.title}</p>
                  <p className="text-sm text-gray-600">{project.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    {project.start_date} - {project.end_date}
                  </p>
                </div>
              </div>
              {project.technologies_used && project.technologies_used.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-600">Technologies:</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {project.technologies_used.map((tech: string, techIndex: number) => (
                      <span key={techIndex} className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {data.personal_information && renderPersonalInfo(data.personal_information)}
      {data.personal_information?.address && renderAddress(data.personal_information.address)}
      {data.professional_summary && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Professional Summary</h3>
          <p className="text-sm text-gray-700">{data.professional_summary}</p>
        </div>
      )}
      {data.work_experience && renderWorkExperience(data.work_experience)}
      {data.education && renderEducation(data.education)}
      {data.skills && renderSkills(data.skills)}
      {data.certifications && renderCertifications(data.certifications)}
      {data.projects && renderProjects(data.projects)}
      {data.awards_and_honors && data.awards_and_honors.length > 0 && (
        <div className="space-y-4">
                              <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-award">🏆</span>
           Awards & Honors
         </h3>
          <div className="space-y-3">
            {data.awards_and_honors.map((award: any, index: number) => (
              <div key={index} className="border-l-4 border-red-500 pl-4">
                <p className="font-semibold text-sm">{award.title}</p>
                <p className="text-sm text-gray-600">{award.issuer}</p>
                <p className="text-sm text-gray-500">{award.date_received}</p>
                <p className="text-sm text-gray-600">{award.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.volunteer_experience && data.volunteer_experience.length > 0 && (
        <div className="space-y-4">
                              <h3 className="text-lg font-semibold flex items-center gap-2">
           <span className="icon icon-users">👥</span>
           Volunteer Experience
         </h3>
          <div className="space-y-4">
            {data.volunteer_experience.map((volunteer: any, index: number) => (
              <div key={index} className="border-l-4 border-orange-500 pl-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-sm">{volunteer.role}</p>
                    <p className="text-sm text-gray-600">{volunteer.organization}</p>
                    <p className="text-sm text-gray-500">{volunteer.location}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {volunteer.start_date} - {volunteer.end_date}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">{volunteer.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.interests && data.interests.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Interests</h3>
          <div className="flex flex-wrap gap-2">
            {data.interests.map((interest: string, index: number) => (
              <span key={index} className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                {interest}
              </span>
            ))}
          </div>
        </div>
      )}
      {data.references && data.references.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">References</h3>
          <div className="space-y-3">
            {data.references.map((ref: any, index: number) => (
              <div key={index} className="border-l-4 border-gray-500 pl-4">
                <p className="font-semibold text-sm">{ref.name}</p>
                <p className="text-sm text-gray-600">{ref.relationship}</p>
                <p className="text-sm text-gray-500">{ref.email}</p>
                <p className="text-sm text-gray-500">{ref.phone}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.additional_information && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Additional Information</h3>
          <p className="text-sm text-gray-700">{data.additional_information}</p>
        </div>
      )}
    </div>
  );
};

export const CVProfilePage: FC = () => {
  const { fileId } = useParams<{ fileId: string }>();
  const navigate = useNavigate();
  const [cvData, setCvData] = useState<CVFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000';

  const generateProfilePDF = async () => {
    if (!cvData?.aiGeneratedJson) {
      alert('No AI generated data available to convert to PDF');
      return;
    }

    try {
      // Get the HTML content of the structured JSON viewer
      const profileContent = document.querySelector('[data-profile-content]');
      if (!profileContent) {
        alert('Could not find profile content to convert');
        return;
      }

      // Get the computed styles for the content
      const styles = window.getComputedStyle(profileContent);
      
      // Create a temporary container with all necessary styles
      const tempContainer = document.createElement('div');
      tempContainer.innerHTML = profileContent.innerHTML;
      tempContainer.style.cssText = `
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #374151;
        background: white;
        padding: 20px;
        max-width: 800px;
        margin: 0 auto;
      `;

             // Add Tailwind-like styles to the content
       const styleElement = document.createElement('style');
       styleElement.textContent = `
         .space-y-4 > * + * { margin-top: 1rem; }
         .space-y-2 > * + * { margin-top: 0.5rem; }
         .space-y-3 > * + * { margin-top: 0.75rem; }
         .space-y-6 > * + * { margin-top: 1.5rem; }
         .space-y-1 > * + * { margin-top: 0.25rem; }
         .gap-2 { gap: 0.5rem; }
         .gap-4 { gap: 1rem; }
         .gap-1 { gap: 0.25rem; }
         .flex { display: flex; }
         .flex-wrap { flex-wrap: wrap; }
         .items-center { align-items: center; }
         .items-start { align-items: flex-start; }
         .justify-between { justify-content: space-between; }
         .justify-start { justify-content: flex-start; }
         .text-right { text-align: right; }
         .grid { display: grid; }
         .grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
         .md\\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
         .md\\:col-span-2 { grid-column: span 2 / span 2; }
         .text-lg { font-size: 1.125rem; line-height: 1.75rem; }
         .text-sm { font-size: 0.875rem; line-height: 1.25rem; }
         .text-xs { font-size: 0.75rem; line-height: 1rem; }
         .font-semibold { font-weight: 600; }
         .font-medium { font-weight: 500; }
         .text-gray-600 { color: #4B5563; }
         .text-gray-500 { color: #6B7280; }
         .text-gray-700 { color: #374151; }
         .text-gray-800 { color: #1F2937; }
         .text-blue-600 { color: #2563EB; }
         .text-green-800 { color: #166534; }
         .text-purple-800 { color: #6B21A8; }
         .text-indigo-800 { color: #3730A3; }
         .text-red-800 { color: #991B1B; }
         .text-orange-800 { color: #9A3412; }
         .text-yellow-800 { color: #92400E; }
         .bg-blue-100 { background-color: #DBEAFE; }
         .bg-green-100 { background-color: #D1FAE5; }
         .bg-purple-100 { background-color: #E9D5FF; }
         .bg-indigo-100 { background-color: #E0E7FF; }
         .bg-gray-100 { background-color: #F3F4F6; }
         .bg-red-100 { background-color: #FEE2E2; }
         .bg-orange-100 { background-color: #FFEDD5; }
         .bg-yellow-100 { background-color: #FEF3C7; }
         .border-l-4 { border-left-width: 4px; }
         .border-blue-500 { border-left-color: #3B82F6; }
         .border-green-500 { border-left-color: #10B981; }
         .border-indigo-500 { border-left-color: #6366F1; }
         .border-red-500 { border-left-color: #EF4444; }
         .border-orange-500 { border-left-color: #F97316; }
         .border-yellow-500 { border-left-color: #EAB308; }
         .border-gray-500 { border-left-color: #6B7280; }
         .pl-4 { padding-left: 1rem; }
         .px-2 { padding-left: 0.5rem; padding-right: 0.5rem; }
         .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
         .mt-1 { margin-top: 0.25rem; }
         .mt-2 { margin-top: 0.5rem; }
         .mb-2 { margin-bottom: 0.5rem; }
         .rounded { border-radius: 0.25rem; }
         .list-disc { list-style-type: disc; }
         .list-inside { list-style-position: inside; }
         .hover\\:underline:hover { text-decoration: underline; }
         .h-5 { height: 1.25rem; }
         .w-5 { width: 1.25rem; }
         .h-4 { height: 1rem; }
         .w-4 { width: 1rem; }
         .h-12 { height: 3rem; }
         .w-12 { width: 3rem; }
         .mx-auto { margin-left: auto; margin-right: auto; }
         .mb-2 { margin-bottom: 0.5rem; }
         .text-center { text-align: center; }
         .py-8 { padding-top: 2rem; padding-bottom: 2rem; }
         .text-gray-500 { color: #6B7280; }
         .overflow-auto { overflow: auto; }
         .space-y-4 > * + * { margin-top: 1rem; }
         .space-y-2 > * + * { margin-top: 0.5rem; }
         .space-y-3 > * + * { margin-top: 0.75rem; }
         .space-y-6 > * + * { margin-top: 1.5rem; }
         .space-y-1 > * + * { margin-top: 0.25rem; }
         
         /* Icon styles using Unicode symbols for better PDF compatibility */
         .icon {
           display: inline-block;
           width: 1.25rem;
           height: 1.25rem;
           margin-right: 0.5rem;
           text-align: center;
           line-height: 1.25rem;
           font-size: 1rem;
           font-weight: bold;
         }
         .icon-user::before { content: "👤"; }
         .icon-briefcase::before { content: "💼"; }
         .icon-graduation::before { content: "🎓"; }
         .icon-star::before { content: "⭐"; }
         .icon-award::before { content: "🏆"; }
         .icon-file-check::before { content: "📋"; }
         .icon-users::before { content: "👥"; }
         .icon-mail::before { content: "📧"; }
         .icon-phone::before { content: "📞"; }
         .icon-map-pin::before { content: "📍"; }
       `;

      const response = await fetch(`${API_BASE_URL}/generate-profile-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileId: cvData.fileId,
          htmlContent: tempContainer.innerHTML,
          cssStyles: styleElement.textContent,
          profileData: cvData.aiGeneratedJson, // Include JSON data as fallback
          originalFilename: cvData.originalFilename
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${cvData.originalFilename}_profile.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  useEffect(() => {
    const fetchCVData = async () => {
      if (!fileId) {
        setError('No file ID provided');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/cv/${fileId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('CV Profile data:', data);
        console.log('Converted PDF filename:', data.convertedPdfFilename);
        console.log('AI Generated JSON:', data.aiGeneratedJson);
        setCvData(data);
      } catch (err) {
        console.error('Error fetching CV data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch CV data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCVData();
  }, [fileId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <PageWrapper className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-2">
          <PageSection index={0}>
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="h-12 w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <FileText className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium">Loading Profile...</h3>
                  <p className="text-sm text-muted-foreground">
                    Please wait while we fetch the candidate profile
                  </p>
                </div>
              </CardContent>
            </Card>
          </PageSection>
        </PageWrapper>
      </div>
    );
  }

  if (error || !cvData) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <PageWrapper className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-2">
          <PageSection index={0}>
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="h-12 w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <FileText className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium">Error loading profile</h3>
                  <p className="text-sm text-muted-foreground">
                    {error || 'Failed to load candidate profile'}
                  </p>
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/cv-list')}
                    className="mt-4"
                  >
                    Back to CV List
                  </Button>
                </div>
              </CardContent>
            </Card>
          </PageSection>
        </PageWrapper>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <PageWrapper className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-2">
        {/* Header Section */}
        <PageSection index={0}>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-4">
                <Link to="/cv-list">
                  <Button variant="ghost" size="sm" className="gap-2">
                    <ArrowLeft className="h-4 w-4" />
                    Back to CV List
                  </Button>
                </Link>
              </div>
            </div>
            
            <div className="space-y-1">
              <h1 className="text-2xl font-bold tracking-tight">Candidate Profile</h1>
              <p className="text-muted-foreground">
                {cvData.originalFilename}
              </p>
            </div>
          </div>
        </PageSection>

        {/* Profile Content */}
        <PageSection index={1}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Side - Converted PDF */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Converted PDF
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-white rounded-lg border h-[calc(100vh-200px)] overflow-hidden">
                  <iframe
                    src={`${API_BASE_URL}/view-pdf/${cvData.fileId}`}
                    className="w-full h-full"
                    title="Converted PDF Viewer"
                    onError={(e) => {
                      console.error('PDF iframe failed to load:', e);
                    }}
                    onLoad={() => {
                      console.log('PDF iframe loaded successfully');
                    }}
                  />
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      try {
                        const pdfUrl = `${API_BASE_URL}/view-pdf/${cvData.fileId}`;
                        console.log('Attempting to open PDF:', pdfUrl);
                        window.open(pdfUrl, '_blank');
                      } catch (error) {
                        console.error('Error opening PDF:', error);
                        alert('Failed to open PDF. Please try downloading instead.');
                      }
                    }}
                    className="gap-2"
                  >
                    <Eye className="h-4 w-4" />
                    Open PDF in New Tab
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      try {
                        const downloadUrl = `${API_BASE_URL}/download-pdf/${cvData.fileId}`;
                        console.log('Attempting to download PDF:', downloadUrl);
                        window.open(downloadUrl, '_blank');
                      } catch (error) {
                        console.error('Error downloading PDF:', error);
                        alert('Failed to download PDF. Please check the file exists.');
                      }
                    }}
                    className="gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download PDF
                  </Button>
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  <p><strong>File ID:</strong> {cvData.fileId}</p>
                  <p><strong>File Type:</strong> {cvData.fileType.toUpperCase()}</p>
                  <p><strong>Status:</strong> {cvData.processingStatus}</p>
                  <p><strong>PDF Filename:</strong> {cvData.convertedPdfFilename || 'Not available'}</p>
                  <p className="text-orange-600 mt-2">
                    <strong>Note:</strong> If PDF viewing fails, try downloading instead
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Right Side - AI Generated JSON */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileJson className="h-5 w-5" />
                  AI Generated Profile Data
                </CardTitle>
              </CardHeader>
              <CardContent>
                {cvData.aiGeneratedJson ? (
                  <div className="space-y-4">
                                         <div className="h-[calc(100vh-200px)] overflow-auto" data-profile-content>
                       <StructuredJSONViewer data={cvData.aiGeneratedJson} />
                     </div>
                                         <div className="flex gap-2">
                       <Button
                         variant="outline"
                         size="sm"
                         className="gap-2"
                         onClick={() => {
                           const blob = new Blob([JSON.stringify(cvData.aiGeneratedJson, null, 2)], {
                             type: 'application/json'
                           });
                           const url = URL.createObjectURL(blob);
                           const a = document.createElement('a');
                           a.href = url;
                           a.download = `${cvData.originalFilename}_ai_generated.json`;
                           document.body.appendChild(a);
                           a.click();
                           document.body.removeChild(a);
                           URL.revokeObjectURL(url);
                         }}
                       >
                         <Download className="h-4 w-4" />
                         Download JSON
                       </Button>
                       <Button
                         variant="default"
                         size="sm"
                         className="gap-2"
                         onClick={generateProfilePDF}
                       >
                         <FileDown className="h-4 w-4" />
                         Generate PDF
                       </Button>
                     </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FileJson className="mx-auto h-12 w-12 mb-2" />
                    <p>AI Generated JSON Not Available</p>
                    <p className="text-sm">The AI processing may still be in progress or failed</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </PageSection>
      </PageWrapper>
    </div>
  );
};
