import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { TypeAheadDropdown } from '@/components/ui/typeahead-dropdown';
import type { TypeAheadOption } from '@/types/system-settings';
import { ArrowLeft, FileText, Download, Eye, Save, User, Mail, Phone, MapPin, Briefcase, GraduationCap, Star, Award, Users, Calendar, Globe, Building, Plus, Trash2 } from 'lucide-react';
import { useState, useEffect, type FC } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useSystemSettings } from '@/hooks/useSystemSettings';

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
  aiGeneratedJson?: any;
  
  // Personal Info
  personalInfo?: {
    firstName?: string;
    middleName?: string;
    lastName?: string;
    birthDate?: string;
    gender?: string;
    civilStatus?: string;
    street?: string;
    barangay?: string;
    city?: string;
    state?: string;
    postalCode?: string;
    country?: string;
    desiredCity?: string;
    desiredState?: string;
    desiredCountry?: string;
    openToWorkFromHome?: boolean;
    openToWorkOnsite?: boolean;
    emails?: Array<{ email: string; emailType?: string; isPrimary?: boolean }>;
    phones?: Array<{ phone: string; phoneType?: string; isPrimary?: boolean }>;
    socialUrls?: Array<{ url: string; platform?: string }>;
  };
  
  // Work Experience
  workExperience?: Array<{
    jobTitle: string;
    companyName?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
    isCurrent?: boolean;
    responsibilities: string[];
  }>;
  
  // Education
  education?: Array<{
    degree: string;
    institution?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
    gpa?: number;
    honors?: string;
  }>;
  
  // Skills
  skills?: Array<{
    skillName: string;
    skillType: string; // 'technical', 'soft', 'language'
    proficiency?: string;
  }>;
  
  // Certifications
  certifications?: Array<{
    name: string;
    issuingOrganization?: string;
    issueDate?: string;
    expirationDate?: string;
  }>;
  
  // Projects
  projects?: Array<{
    title: string;
    description?: string;
    startDate?: string;
    endDate?: string;
    projectUrl?: string;
    technologies: string[];
  }>;
  
  // Awards & Honors
  awardsHonors?: Array<{
    title: string;
    issuingOrganization?: string;
    dateReceived?: string;
    description?: string;
  }>;
  
  // Volunteer Experience
  volunteerExperience?: Array<{
    role: string;
    organization?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
    description?: string;
  }>;
  
  // References
  references?: Array<{
    name: string;
    relationship?: string;
    email?: string;
    phone?: string;
  }>;
  
  // IT Systems
  itSystems?: Array<{
    systemName: string;
    abbreviation?: string;
  }>;
}

export const EditCandidatePage: FC = () => {
  const { fileId } = useParams<{ fileId: string }>();
  const navigate = useNavigate();
  const [cvData, setCvData] = useState<CVFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // System settings hook
  const { getSettingsByCategory, loading: settingsLoading } = useSystemSettings();

  const API_BASE_URL = 'http://localhost:8000';

  // Form data state - comprehensive form data
  const [editFormData, setEditFormData] = useState({
    // Personal Info
    firstName: '',
    middleName: '',
    lastName: '',
    birthDate: '',
    gender: '',
    civilStatus: '',
    street: '',
    barangay: '',
    city: '',
    state: '',
    postalCode: '',
    country: '',
    desiredCity: '',
    desiredState: '',
    desiredCountry: '',
    openToWorkFromHome: false,
    openToWorkOnsite: false,
    
    // Contact Info
    emails: [{ email: '', emailType: 'personal', isPrimary: true }],
    phones: [{ phone: '', phoneType: 'mobile', isPrimary: true }],
    socialUrls: [{ url: '', platform: '' }],
    
    // Work Experience
    workExperience: [{
      jobTitle: '',
      companyName: '',
      location: '',
      startDate: '',
      endDate: '',
      isCurrent: false,
      responsibilities: ['']
    }],
    
         // Education
     education: [{
       degree: '',
       institution: '',
       location: '',
       startDate: '',
       endDate: '',
       gpa: undefined,
       honors: ''
     }],
    
    // Skills
    skills: [{
      skillName: '',
      skillType: 'technical',
      proficiency: ''
    }],
    
    // Certifications
    certifications: [{
      name: '',
      issuingOrganization: '',
      issueDate: '',
      expirationDate: ''
    }],
    
    // Projects
    projects: [{
      title: '',
      description: '',
      startDate: '',
      endDate: '',
      projectUrl: '',
      technologies: ['']
    }],
    
    // Awards & Honors
    awardsHonors: [{
      title: '',
      issuingOrganization: '',
      dateReceived: '',
      description: ''
    }],
    
    // Volunteer Experience
    volunteerExperience: [{
      role: '',
      organization: '',
      location: '',
      startDate: '',
      endDate: '',
      description: ''
    }],
    
    // References
    references: [{
      name: '',
      relationship: '',
      email: '',
      phone: ''
    }],
    
    // IT Systems
    itSystems: [{
      systemName: '',
      abbreviation: ''
    }]
  });

  // Fetch CV data on component mount
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
        console.log('CV Edit data:', data);
        setCvData(data);

        // Initialize form data with current values
        setEditFormData({
          // Personal Info
          firstName: data.personalInfo?.firstName || '',
          middleName: data.personalInfo?.middleName || '',
          lastName: data.personalInfo?.lastName || '',
          birthDate: data.personalInfo?.birthDate ? new Date(data.personalInfo.birthDate).toISOString().split('T')[0] : '',
          gender: data.personalInfo?.gender || '',
          civilStatus: data.personalInfo?.civilStatus || '',
          street: data.personalInfo?.street || '',
          barangay: data.personalInfo?.barangay || '',
          city: data.personalInfo?.city || '',
          state: data.personalInfo?.state || '',
          postalCode: data.personalInfo?.postalCode || '',
          country: data.personalInfo?.country || '',
          desiredCity: data.personalInfo?.desiredCity || '',
          desiredState: data.personalInfo?.desiredState || '',
          desiredCountry: data.personalInfo?.desiredCountry || '',
          openToWorkFromHome: data.personalInfo?.openToWorkFromHome || false,
          openToWorkOnsite: data.personalInfo?.openToWorkOnsite || false,
          
          // Contact Info
          emails: data.personalInfo?.emails?.length > 0 ? data.personalInfo.emails : [{ email: '', emailType: 'personal', isPrimary: true }],
          phones: data.personalInfo?.phones?.length > 0 ? data.personalInfo.phones : [{ phone: '', phoneType: 'mobile', isPrimary: true }],
          socialUrls: data.personalInfo?.socialUrls?.length > 0 ? data.personalInfo.socialUrls : [{ url: '', platform: '' }],
          
          // Work Experience
          workExperience: data.workExperience?.length > 0 ? data.workExperience.map((exp: any) => ({
            ...exp,
            startDate: exp.startDate ? new Date(exp.startDate).toISOString().split('T')[0] : '',
            endDate: exp.endDate ? new Date(exp.endDate).toISOString().split('T')[0] : ''
          })) : [{
            jobTitle: '',
            companyName: '',
            location: '',
            startDate: '',
            endDate: '',
            isCurrent: false,
            responsibilities: ['']
          }],
          
          // Education
          education: data.education?.length > 0 ? data.education.map((edu: any) => ({
            ...edu,
            startDate: edu.startDate ? new Date(edu.startDate).toISOString().split('T')[0] : '',
            endDate: edu.endDate ? new Date(edu.endDate).toISOString().split('T')[0] : '',
            gpa: edu.gpa ? parseFloat(edu.gpa.toString()) : undefined
          })) : [{
            degree: '',
            institution: '',
            location: '',
            startDate: '',
            endDate: '',
            gpa: undefined,
            honors: ''
          }],
          
          // Skills
          skills: data.skills?.length > 0 ? data.skills : [{
            skillName: '',
            skillType: 'technical',
            proficiency: ''
          }],
          
          // Certifications
          certifications: data.certifications?.length > 0 ? data.certifications.map((cert: any) => ({
            ...cert,
            issueDate: cert.issueDate ? new Date(cert.issueDate).toISOString().split('T')[0] : '',
            expirationDate: cert.expirationDate ? new Date(cert.expirationDate).toISOString().split('T')[0] : ''
          })) : [{
            name: '',
            issuingOrganization: '',
            issueDate: '',
            expirationDate: ''
          }],
          
          // Projects
          projects: data.projects?.length > 0 ? data.projects.map((proj: any) => ({
            ...proj,
            startDate: proj.startDate ? new Date(proj.startDate).toISOString().split('T')[0] : '',
            endDate: proj.endDate ? new Date(proj.endDate).toISOString().split('T')[0] : ''
          })) : [{
            title: '',
            description: '',
            startDate: '',
            endDate: '',
            projectUrl: '',
            technologies: ['']
          }],
          
          // Awards & Honors
          awardsHonors: data.awardsHonors?.length > 0 ? data.awardsHonors.map((award: any) => ({
            ...award,
            dateReceived: award.dateReceived ? new Date(award.dateReceived).toISOString().split('T')[0] : ''
          })) : [{
            title: '',
            issuingOrganization: '',
            dateReceived: '',
            description: ''
          }],
          
          // Volunteer Experience
          volunteerExperience: data.volunteerExperience?.length > 0 ? data.volunteerExperience.map((vol: any) => ({
            ...vol,
            startDate: vol.startDate ? new Date(vol.startDate).toISOString().split('T')[0] : '',
            endDate: vol.endDate ? new Date(vol.endDate).toISOString().split('T')[0] : ''
          })) : [{
            role: '',
            organization: '',
            location: '',
            startDate: '',
            endDate: '',
            description: ''
          }],
          
          // References
          references: data.references?.length > 0 ? data.references : [{
            name: '',
            relationship: '',
            email: '',
            phone: ''
          }],
          
          // IT Systems
          itSystems: data.itSystems?.length > 0 ? data.itSystems : [{
            systemName: '',
            abbreviation: ''
          }]
        });
      } catch (err) {
        console.error('Error fetching CV data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch CV data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCVData();
  }, [fileId]);

  const handleSaveEdit = async () => {
    if (!cvData) {
      toast.error('No CV data available');
      return;
    }

    try {
      setIsSaving(true);

      // Prepare the updated data
      const updatedData = {
        personalInfo: {
          firstName: editFormData.firstName,
          middleName: editFormData.middleName,
          lastName: editFormData.lastName,
          birthDate: editFormData.birthDate,
          gender: editFormData.gender,
          civilStatus: editFormData.civilStatus,
          street: editFormData.street,
          barangay: editFormData.barangay,
          city: editFormData.city,
          state: editFormData.state,
          postalCode: editFormData.postalCode,
          country: editFormData.country,
          desiredCity: editFormData.desiredCity,
          desiredState: editFormData.desiredState,
          desiredCountry: editFormData.desiredCountry,
          openToWorkFromHome: editFormData.openToWorkFromHome,
          openToWorkOnsite: editFormData.openToWorkOnsite,
          emails: editFormData.emails.filter(email => email.email.trim() !== ''),
          phones: editFormData.phones.filter(phone => phone.phone.trim() !== ''),
          socialUrls: editFormData.socialUrls.filter(social => social.url.trim() !== '')
        },
        workExperience: editFormData.workExperience.filter(exp => exp.jobTitle.trim() !== ''),
        education: editFormData.education.filter(edu => edu.degree.trim() !== ''),
        skills: editFormData.skills.filter(skill => skill.skillName.trim() !== ''),
        certifications: editFormData.certifications.filter(cert => cert.name.trim() !== ''),
        projects: editFormData.projects.filter(proj => proj.title.trim() !== ''),
        awardsHonors: editFormData.awardsHonors.filter(award => award.title.trim() !== ''),
        volunteerExperience: editFormData.volunteerExperience.filter(vol => vol.role.trim() !== ''),
        references: editFormData.references.filter(ref => ref.name.trim() !== ''),
        itSystems: editFormData.itSystems.filter(sys => sys.systemName.trim() !== '')
      };

      // Update the CV data in the backend
      const response = await fetch(`${API_BASE_URL}/cv/${cvData.fileId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedDataResponse = await response.json();
      
      // Update local state
      setCvData({
        ...cvData,
        ...updatedData
      });

      toast.success('Candidate details updated successfully!');
      
      // Navigate back to CV list
      navigate('/cv-list');
    } catch (error) {
      console.error('Error updating CV:', error);
      toast.error('Failed to update candidate details');
    } finally {
      setIsSaving(false);
    }
  };

  // Helper functions for dynamic form arrays
  const addArrayItem = (field: keyof typeof editFormData, template: any) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: [...(prev[field] as any[]), template]
    }));
  };

  const removeArrayItem = (field: keyof typeof editFormData, index: number) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: (prev[field] as any[]).filter((_, i) => i !== index)
    }));
  };

  const updateArrayItem = (field: keyof typeof editFormData, index: number, value: any) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: (prev[field] as any[]).map((item, i) => i === index ? value : item)
    }));
  };

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
                  <h3 className="font-medium">Loading Candidate Data...</h3>
                  <p className="text-sm text-muted-foreground">
                    Please wait while we fetch the candidate information
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
                  <h3 className="font-medium">Error loading candidate data</h3>
                  <p className="text-sm text-muted-foreground">
                    {error || 'Failed to load candidate information'}
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
      <PageWrapper className="mx-auto max-w-full px-2 sm:px-4 lg:px-6 py-2">
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
              <h1 className="text-2xl font-bold tracking-tight">Edit Candidate Details</h1>
              <p className="text-muted-foreground">
                {cvData.originalFilename}
              </p>
            </div>
          </div>
        </PageSection>

                 {/* Edit Content */}
         <PageSection index={1}>
           <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
             {/* Left Side - PDF Viewer - Sticky */}
             <div className="lg:sticky lg:top-4 lg:self-start">
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <FileText className="h-5 w-5" />
                     Original PDF Reference
                   </CardTitle>
                 </CardHeader>
                 <CardContent>
                   {cvData.convertedPdfFilename ? (
                     <div className="bg-white rounded-lg border h-[600px] overflow-hidden">
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
                   ) : (
                     <div className="bg-muted rounded-lg h-[400px] flex items-center justify-center">
                       <div className="text-center space-y-4">
                         <div className="text-muted-foreground">
                           <FileText className="h-16 w-16 mx-auto mb-4" />
                           <p className="text-sm font-medium">PDF Not Available</p>
                           <p className="text-xs text-muted-foreground mt-1">
                             Converted PDF not found in database
                           </p>
                         </div>
                       </div>
                     </div>
                   )}
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
                           toast.error('Failed to open PDF. Please try downloading instead.');
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
                           toast.error('Failed to download PDF. Please check the file exists.');
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
                   </div>
                 </CardContent>
               </Card>
             </div>

            {/* Right Side - Edit Form */}
            <div className="space-y-6">
              {/* Personal Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Personal Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Name Fields */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">First Name</label>
                        <Input
                          value={editFormData.firstName}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, firstName: e.target.value }))}
                          placeholder="First Name"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Middle Name</label>
                        <Input
                          value={editFormData.middleName}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, middleName: e.target.value }))}
                          placeholder="Middle Name"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Last Name</label>
                        <Input
                          value={editFormData.lastName}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, lastName: e.target.value }))}
                          placeholder="Last Name"
                        />
                      </div>
                    </div>

                    {/* Personal Details */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">Birth Date</label>
                        <Input
                          type="date"
                          value={editFormData.birthDate}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, birthDate: e.target.value }))}
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Gender</label>
                        <TypeAheadDropdown
                          options={getSettingsByCategory('gender')}
                          value={editFormData.gender}
                          onChange={(value) => setEditFormData(prev => ({ ...prev, gender: value }))}
                          placeholder="Select gender"
                          allowCustom={true}
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Civil Status</label>
                        <TypeAheadDropdown
                          options={getSettingsByCategory('civil_status')}
                          value={editFormData.civilStatus}
                          onChange={(value) => setEditFormData(prev => ({ ...prev, civilStatus: value }))}
                          placeholder="Select civil status"
                          allowCustom={true}
                        />
                      </div>
                    </div>

                    {/* Address */}
                    <div>
                      <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        Current Address
                      </label>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          value={editFormData.street}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, street: e.target.value }))}
                          placeholder="Street Address"
                        />
                        <Input
                          value={editFormData.barangay}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, barangay: e.target.value }))}
                          placeholder="Barangay"
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-4 mt-2">
                        <Input
                          value={editFormData.city}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, city: e.target.value }))}
                          placeholder="City"
                        />
                        <Input
                          value={editFormData.state}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, state: e.target.value }))}
                          placeholder="State/Province"
                        />
                        <Input
                          value={editFormData.postalCode}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, postalCode: e.target.value }))}
                          placeholder="Postal Code"
                        />
                      </div>
                      <Input
                        value={editFormData.country}
                        onChange={(e) => setEditFormData(prev => ({ ...prev, country: e.target.value }))}
                        placeholder="Country"
                        className="mt-2"
                      />
                    </div>

                    {/* Desired Location */}
                    <div>
                      <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Desired Work Location
                      </label>
                      <div className="grid grid-cols-3 gap-4">
                        <Input
                          value={editFormData.desiredCity}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, desiredCity: e.target.value }))}
                          placeholder="Desired City"
                        />
                        <Input
                          value={editFormData.desiredState}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, desiredState: e.target.value }))}
                          placeholder="Desired State"
                        />
                        <Input
                          value={editFormData.desiredCountry}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, desiredCountry: e.target.value }))}
                          placeholder="Desired Country"
                        />
                      </div>
                    </div>

                    {/* Work Preferences */}
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={editFormData.openToWorkFromHome}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, openToWorkFromHome: e.target.checked }))}
                        />
                        <span className="text-sm">Open to Remote Work</span>
                      </label>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={editFormData.openToWorkOnsite}
                          onChange={(e) => setEditFormData(prev => ({ ...prev, openToWorkOnsite: e.target.checked }))}
                        />
                        <span className="text-sm">Open to On-site Work</span>
                      </label>
                    </div>
                  </div>
                </CardContent>
              </Card>

                             {/* Contact Information */}
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <Mail className="h-5 w-5" />
                     Contact Information
                   </CardTitle>
                 </CardHeader>
                 <CardContent>
                   <div className="space-y-4">
                     {/* Emails */}
                     <div>
                       <div className="flex items-center justify-between mb-2">
                         <label className="text-sm font-medium">Email Addresses</label>
                         <Button
                           type="button"
                           variant="outline"
                           size="sm"
                           onClick={() => addArrayItem('emails', { email: '', emailType: 'personal', isPrimary: false })}
                         >
                           <Plus className="h-4 w-4" />
                         </Button>
                       </div>
                       {editFormData.emails.map((email, index) => (
                         <div key={index} className="flex gap-2 mb-2">
                           <Input
                             value={email.email}
                             onChange={(e) => updateArrayItem('emails', index, { ...email, email: e.target.value })}
                             placeholder="Email address"
                             className="flex-1"
                           />
                           <TypeAheadDropdown
                             options={getSettingsByCategory('email_types')}
                             value={email.emailType}
                             onChange={(value) => updateArrayItem('emails', index, { ...email, emailType: value })}
                             placeholder="Select email type"
                             allowCustom={true}
                             className="min-w-[140px]"
                           />
                           <label className="flex items-center gap-1">
                             <input
                               type="checkbox"
                               checked={email.isPrimary}
                               onChange={(e) => updateArrayItem('emails', index, { ...email, isPrimary: e.target.checked })}
                             />
                             <span className="text-xs">Primary</span>
                           </label>
                           {editFormData.emails.length > 1 && (
                             <Button
                               type="button"
                               variant="outline"
                               size="sm"
                               onClick={() => removeArrayItem('emails', index)}
                             >
                               <Trash2 className="h-4 w-4" />
                             </Button>
                           )}
                         </div>
                       ))}
                     </div>

                     {/* Phones */}
                     <div>
                       <div className="flex items-center justify-between mb-2">
                         <label className="text-sm font-medium">Phone Numbers</label>
                         <Button
                           type="button"
                           variant="outline"
                           size="sm"
                           onClick={() => addArrayItem('phones', { phone: '', phoneType: 'mobile', isPrimary: false })}
                         >
                           <Plus className="h-4 w-4" />
                         </Button>
                       </div>
                       {editFormData.phones.map((phone, index) => (
                         <div key={index} className="flex gap-2 mb-2">
                           <Input
                             value={phone.phone}
                             onChange={(e) => updateArrayItem('phones', index, { ...phone, phone: e.target.value })}
                             placeholder="Phone number"
                             className="flex-1"
                           />
                           <TypeAheadDropdown
                             options={getSettingsByCategory('phone_types')}
                             value={phone.phoneType}
                             onChange={(value) => updateArrayItem('phones', index, { ...phone, phoneType: value })}
                             placeholder="Select phone type"
                             allowCustom={true}
                             className="min-w-[140px]"
                           />
                           <label className="flex items-center gap-1">
                             <input
                               type="checkbox"
                               checked={phone.isPrimary}
                               onChange={(e) => updateArrayItem('phones', index, { ...phone, isPrimary: e.target.checked })}
                             />
                             <span className="text-xs">Primary</span>
                           </label>
                           {editFormData.phones.length > 1 && (
                             <Button
                               type="button"
                               variant="outline"
                               size="sm"
                               onClick={() => removeArrayItem('phones', index)}
                             >
                               <Trash2 className="h-4 w-4" />
                             </Button>
                           )}
                         </div>
                       ))}
                     </div>

                     {/* Social URLs */}
                     <div>
                       <div className="flex items-center justify-between mb-2">
                         <label className="text-sm font-medium">Social Media</label>
                         <Button
                           type="button"
                           variant="outline"
                           size="sm"
                           onClick={() => addArrayItem('socialUrls', { url: '', platform: '' })}
                         >
                           <Plus className="h-4 w-4" />
                         </Button>
                       </div>
                       {editFormData.socialUrls.map((social, index) => (
                         <div key={index} className="flex gap-2 mb-2">
                           <Input
                             value={social.url}
                             onChange={(e) => updateArrayItem('socialUrls', index, { ...social, url: e.target.value })}
                             placeholder="URL"
                             className="flex-1"
                           />
                           <TypeAheadDropdown
                             options={getSettingsByCategory('social_platforms')}
                             value={social.platform}
                             onChange={(value) => updateArrayItem('socialUrls', index, { ...social, platform: value })}
                             placeholder="Select platform"
                             allowCustom={true}
                             className="flex-1"
                           />
                           {editFormData.socialUrls.length > 1 && (
                             <Button
                               type="button"
                               variant="outline"
                               size="sm"
                               onClick={() => removeArrayItem('socialUrls', index)}
                             >
                               <Trash2 className="h-4 w-4" />
                             </Button>
                           )}
                         </div>
                       ))}
                     </div>
                   </div>
                 </CardContent>
               </Card>

               {/* Work Experience */}
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <Briefcase className="h-5 w-5" />
                     Work Experience
                   </CardTitle>
                 </CardHeader>
                 <CardContent>
                   <div className="space-y-4">
                     {editFormData.workExperience.map((experience, index) => (
                       <div key={index} className="border rounded-lg p-4 space-y-4">
                         <div className="flex items-center justify-between">
                           <h4 className="font-medium">Experience #{index + 1}</h4>
                           {editFormData.workExperience.length > 1 && (
                             <Button
                               type="button"
                               variant="outline"
                               size="sm"
                               onClick={() => removeArrayItem('workExperience', index)}
                             >
                               <Trash2 className="h-4 w-4" />
                             </Button>
                           )}
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Job Title *</label>
                             <Input
                               value={experience.jobTitle}
                               onChange={(e) => updateArrayItem('workExperience', index, { ...experience, jobTitle: e.target.value })}
                               placeholder="Software Engineer"
                             />
                           </div>
                           <div>
                             <label className="text-sm font-medium mb-2 block">Company Name</label>
                             <Input
                               value={experience.companyName}
                               onChange={(e) => updateArrayItem('workExperience', index, { ...experience, companyName: e.target.value })}
                               placeholder="Company Inc."
                             />
                           </div>
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Location</label>
                             <Input
                               value={experience.location}
                               onChange={(e) => updateArrayItem('workExperience', index, { ...experience, location: e.target.value })}
                               placeholder="City, Country"
                             />
                           </div>
                           <div className="flex items-center gap-2">
                             <label className="flex items-center gap-2">
                               <input
                                 type="checkbox"
                                 checked={experience.isCurrent}
                                 onChange={(e) => updateArrayItem('workExperience', index, { ...experience, isCurrent: e.target.checked })}
                               />
                               <span className="text-sm">Current Position</span>
                             </label>
                           </div>
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Start Date</label>
                             <Input
                               type="date"
                               value={experience.startDate}
                               onChange={(e) => updateArrayItem('workExperience', index, { ...experience, startDate: e.target.value })}
                             />
                           </div>
                           <div>
                             <label className="text-sm font-medium mb-2 block">End Date</label>
                             <Input
                               type="date"
                               value={experience.endDate}
                               onChange={(e) => updateArrayItem('workExperience', index, { ...experience, endDate: e.target.value })}
                               disabled={experience.isCurrent}
                             />
                           </div>
                         </div>
                         
                         <div>
                           <label className="text-sm font-medium mb-2 block">Responsibilities</label>
                           {experience.responsibilities.map((responsibility, respIndex) => (
                             <div key={respIndex} className="flex gap-2 mb-2">
                               <Input
                                 value={responsibility}
                                 onChange={(e) => {
                                   const newResponsibilities = [...experience.responsibilities];
                                   newResponsibilities[respIndex] = e.target.value;
                                   updateArrayItem('workExperience', index, { ...experience, responsibilities: newResponsibilities });
                                 }}
                                 placeholder="Describe your responsibilities"
                                 className="flex-1"
                               />
                               {experience.responsibilities.length > 1 && (
                                 <Button
                                   type="button"
                                   variant="outline"
                                   size="sm"
                                   onClick={() => {
                                     const newResponsibilities = experience.responsibilities.filter((_, i) => i !== respIndex);
                                     updateArrayItem('workExperience', index, { ...experience, responsibilities: newResponsibilities });
                                   }}
                                 >
                                   <Trash2 className="h-4 w-4" />
                                 </Button>
                               )}
                             </div>
                           ))}
                           <Button
                             type="button"
                             variant="outline"
                             size="sm"
                             onClick={() => {
                               const newResponsibilities = [...experience.responsibilities, ''];
                               updateArrayItem('workExperience', index, { ...experience, responsibilities: newResponsibilities });
                             }}
                             className="mt-2"
                           >
                             <Plus className="h-4 w-4 mr-2" />
                             Add Responsibility
                           </Button>
                         </div>
                       </div>
                     ))}
                     
                     <Button
                       type="button"
                       variant="outline"
                       onClick={() => addArrayItem('workExperience', {
                         jobTitle: '',
                         companyName: '',
                         location: '',
                         startDate: '',
                         endDate: '',
                         isCurrent: false,
                         responsibilities: ['']
                       })}
                     >
                       <Plus className="h-4 w-4 mr-2" />
                       Add Work Experience
                     </Button>
                   </div>
                 </CardContent>
               </Card>

               {/* Education */}
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <GraduationCap className="h-5 w-5" />
                     Education
                   </CardTitle>
                 </CardHeader>
                 <CardContent>
                   <div className="space-y-4">
                     {editFormData.education.map((edu, index) => (
                       <div key={index} className="border rounded-lg p-4 space-y-4">
                         <div className="flex items-center justify-between">
                           <h4 className="font-medium">Education #{index + 1}</h4>
                           {editFormData.education.length > 1 && (
                             <Button
                               type="button"
                               variant="outline"
                               size="sm"
                               onClick={() => removeArrayItem('education', index)}
                             >
                               <Trash2 className="h-4 w-4" />
                             </Button>
                           )}
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Degree *</label>
                             <Input
                               value={edu.degree}
                               onChange={(e) => updateArrayItem('education', index, { ...edu, degree: e.target.value })}
                               placeholder="Bachelor of Science in Computer Science"
                             />
                           </div>
                           <div>
                             <label className="text-sm font-medium mb-2 block">Institution</label>
                             <Input
                               value={edu.institution}
                               onChange={(e) => updateArrayItem('education', index, { ...edu, institution: e.target.value })}
                               placeholder="University Name"
                             />
                           </div>
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Location</label>
                             <Input
                               value={edu.location}
                               onChange={(e) => updateArrayItem('education', index, { ...edu, location: e.target.value })}
                               placeholder="City, Country"
                             />
                           </div>
                                                        <div>
                               <label className="text-sm font-medium mb-2 block">GPA</label>
                               <Input
                                 type="number"
                                 step="0.01"
                                 min="0"
                                 max="4"
                                 value={edu.gpa || ''}
                                 onChange={(e) => updateArrayItem('education', index, { ...edu, gpa: e.target.value ? parseFloat(e.target.value) : undefined })}
                                 placeholder="3.8"
                               />
                             </div>
                         </div>
                         
                         <div className="grid grid-cols-2 gap-4">
                           <div>
                             <label className="text-sm font-medium mb-2 block">Start Date</label>
                             <Input
                               type="date"
                               value={edu.startDate}
                               onChange={(e) => updateArrayItem('education', index, { ...edu, startDate: e.target.value })}
                             />
                           </div>
                           <div>
                             <label className="text-sm font-medium mb-2 block">End Date</label>
                             <Input
                               type="date"
                               value={edu.endDate}
                               onChange={(e) => updateArrayItem('education', index, { ...edu, endDate: e.target.value })}
                             />
                           </div>
                         </div>
                         
                         <div>
                           <label className="text-sm font-medium mb-2 block">Honors/Awards</label>
                           <Input
                             value={edu.honors}
                             onChange={(e) => updateArrayItem('education', index, { ...edu, honors: e.target.value })}
                             placeholder="Magna Cum Laude, Dean's List, etc."
                           />
                         </div>
                       </div>
                     ))}
                     
                     <Button
                       type="button"
                       variant="outline"
                       onClick={() => addArrayItem('education', {
                         degree: '',
                         institution: '',
                         location: '',
                         startDate: '',
                         endDate: '',
                         gpa: '',
                         honors: ''
                       })}
                     >
                       <Plus className="h-4 w-4 mr-2" />
                       Add Education
                     </Button>
                   </div>
                 </CardContent>
               </Card>

               {/* Skills */}
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <Star className="h-5 w-5" />
                     Skills
                   </CardTitle>
                 </CardHeader>
                 <CardContent>
                   <div className="space-y-4">
                     {editFormData.skills.map((skill, index) => (
                       <div key={index} className="flex gap-2 items-end">
                         <div className="flex-1">
                           <label className="text-sm font-medium mb-2 block">Skill Name *</label>
                           <Input
                             value={skill.skillName}
                             onChange={(e) => updateArrayItem('skills', index, { ...skill, skillName: e.target.value })}
                             placeholder="JavaScript, Project Management, etc."
                           />
                         </div>
                         <div className="w-32">
                           <label className="text-sm font-medium mb-2 block">Type</label>
                           <TypeAheadDropdown
                             options={getSettingsByCategory('skill_categories')}
                             value={skill.skillType}
                             onChange={(value) => updateArrayItem('skills', index, { ...skill, skillType: value })}
                             placeholder="Select type"
                             allowCustom={true}
                           />
                         </div>
                         <div className="w-32">
                           <label className="text-sm font-medium mb-2 block">Proficiency</label>
                           <TypeAheadDropdown
                             options={getSettingsByCategory('proficiency_levels')}
                             value={skill.proficiency}
                             onChange={(value) => updateArrayItem('skills', index, { ...skill, proficiency: value })}
                             placeholder="Select level"
                             allowCustom={true}
                           />
                         </div>
                         {editFormData.skills.length > 1 && (
                           <Button
                             type="button"
                             variant="outline"
                             size="sm"
                             onClick={() => removeArrayItem('skills', index)}
                           >
                             <Trash2 className="h-4 w-4" />
                           </Button>
                         )}
                       </div>
                     ))}
                     
                     <Button
                       type="button"
                       variant="outline"
                       onClick={() => addArrayItem('skills', {
                         skillName: '',
                         skillType: 'technical',
                         proficiency: ''
                       })}
                     >
                       <Plus className="h-4 w-4 mr-2" />
                       Add Skill
                     </Button>
                   </div>
                 </CardContent>
               </Card>

               {/* Action Buttons */}
               <div className="flex gap-2 pt-4">
                 <Button
                   variant="outline"
                   onClick={() => navigate('/cv-list')}
                 >
                   Cancel
                 </Button>
                 <Button 
                   onClick={handleSaveEdit}
                   disabled={isSaving}
                   className="gap-2"
                 >
                   {isSaving ? (
                     <>
                       <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                       Saving...
                     </>
                   ) : (
                     <>
                       <Save className="h-4 w-4" />
                       Save Changes
                     </>
                   )}
                 </Button>
               </div>
            </div>
          </div>
        </PageSection>
      </PageWrapper>
    </div>
  );
};
