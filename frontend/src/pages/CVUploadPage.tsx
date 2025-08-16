import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Upload, FileText, Download, AlertCircle, CheckCircle, ArrowLeft, FileJson, Loader2, Trash2, X, Square } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { Link } from 'react-router-dom';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  currentStep?: string; // For processing steps
  error?: string;
  pdfUrl?: string;
  extractedText?: string;
  originalFilename?: string;
  fileId?: string; // Database file ID
  aiOutput?: any; // Store the AI-generated JSON output (legacy)
  aiGeneratedJson?: any; // Store the AI-generated JSON from database
  aiPdfUrl?: string; // Store the AI-generated PDF URL
}

interface JsonErrorDetails {
  error: boolean;
  error_message: string;
  raw_ai_response?: string;
  filename?: string;
  text_content_preview?: string;
  can_retry?: boolean;
}

type ViewMode = 'extracted_text' | 'json_output' | 'ai_pdf';

// Component to render structured JSON data (copied from CVProfilePage)
const StructuredJSONViewer: React.FC<{ data: any }> = ({ data }) => {
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
            </div>
          ))}
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
    </div>
  );
};

const CVUploadPage = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [jsonErrorDetails, setJsonErrorDetails] = useState<JsonErrorDetails | null>(null);
  const [currentJsonFile, setCurrentJsonFile] = useState<UploadedFile | null>(null);
  const [isProcessingJson, setIsProcessingJson] = useState(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [currentViewMode, setCurrentViewMode] = useState<ViewMode>('extracted_text');
  const [pdfLoadError, setPdfLoadError] = useState<boolean>(false);
  
  // Track polling intervals for stop functionality
  const [pollingIntervals, setPollingIntervals] = useState<Map<string, NodeJS.Timeout>>(new Map());
  
  // Duplicate file modal state
  const [duplicateModalOpen, setDuplicateModalOpen] = useState(false);
  const [duplicateFileData, setDuplicateFileData] = useState<{
    file: UploadedFile;
    originalFile: File;
    duplicateFileId: string;
    duplicateFilename: string;
  } | null>(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Function to add a polling interval
  const addPollingInterval = (fileId: string, interval: NodeJS.Timeout) => {
    setPollingIntervals(prev => new Map(prev).set(fileId, interval));
  };

  // Function to remove a polling interval
  const removePollingInterval = (fileId: string) => {
    setPollingIntervals(prev => {
      const newMap = new Map(prev);
      const interval = newMap.get(fileId);
      if (interval) {
        clearInterval(interval);
        newMap.delete(fileId);
      }
      return newMap;
    });
  };

  // Function to stop processing for a specific file
  const stopFileProcessing = async (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (!file) return;

    // Check if file has a fileId (database ID)
    if (!file.fileId) {
      // If no fileId, just stop the frontend polling and update status
      removePollingInterval(fileId);
      
      setFiles(prev => prev.map(f => 
        f.id === fileId ? {
          ...f,
          status: 'error',
          error: 'Processing stopped by user (no backend file ID)',
          progress: 0,
          currentStep: 'Processing stopped'
        } : f
      ));
      
      toast.success(`Processing stopped for ${file.name}`);
      return;
    }

    try {
      // Call backend to stop processing
      const response = await fetch(`${API_BASE_URL}/cv/${file.fileId}/stop`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to stop processing');
      }

      // Clear the polling interval
      removePollingInterval(fileId);
      
      // Update file status to stopped
      setFiles(prev => prev.map(f => 
        f.id === fileId ? {
          ...f,
          status: 'error',
          error: 'Processing stopped by user',
          progress: 0,
          currentStep: 'Processing stopped'
        } : f
      ));
      
      toast.success(`Processing stopped for ${file.name}`);
      
    } catch (error) {
      console.error('Error stopping processing:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to stop processing';
      toast.error(`Failed to stop processing: ${errorMessage}`);
    }
  };

  // Cleanup polling intervals on component unmount
  useEffect(() => {
    return () => {
      pollingIntervals.forEach((interval) => {
        clearInterval(interval);
      });
    };
  }, [pollingIntervals]);

  // Handle duplicate file actions
  const handleDuplicateDeleteAndReupload = async () => {
    if (!duplicateFileData) return;
    
    const { file, originalFile, duplicateFileId } = duplicateFileData;
    
    console.log('🔄 Starting duplicate file delete and reprocess:', {
      fileId: file.id,
      fileName: file.name,
      duplicateFileId,
      duplicateFileIdType: typeof duplicateFileId,
      duplicateFileIdLength: duplicateFileId?.length,
      originalFileName: originalFile.name
    });
    
    try {
      // Delete the existing file
      console.log('🗑️ Deleting existing file:', duplicateFileId);
      const deleteResponse = await fetch(`${API_BASE_URL}/cv/${duplicateFileId}`, {
        method: 'DELETE',
      });
      
      if (!deleteResponse.ok) {
        const errorText = await deleteResponse.text();
        console.error('❌ Delete failed:', deleteResponse.status, errorText);
        throw new Error(`Failed to delete existing file: ${deleteResponse.statusText}`);
      }
      
      const deleteResult = await deleteResponse.json();
      console.log('✅ Existing file deleted:', deleteResult);
      
      // Now reprocess the uploaded file
      console.log('🔄 Starting reprocess for file:', originalFile.name);
      const reprocessFormData = new FormData();
      reprocessFormData.append('file', originalFile);
      
      const reprocessResponse = await fetch(`${API_BASE_URL}/cv/reprocess`, {
        method: 'POST',
        body: reprocessFormData,
      });
      
      if (!reprocessResponse.ok) {
        const errorText = await reprocessResponse.text();
        console.error('❌ Reprocess failed:', reprocessResponse.status, errorText);
        throw new Error(`Failed to reprocess file: ${reprocessResponse.statusText}`);
      }
      
      const reprocessResult = await reprocessResponse.json();
      console.log('🔄 File reprocessing result:', reprocessResult);
      
      // Check if reprocessing completed immediately
      if (reprocessResult.success && reprocessResult.processing_status === 'completed') {
        console.log('✅ Reprocessing completed immediately');
        
        // Update file status to completed
        const updatedFile = {
          ...file,
          status: 'completed' as const,
          progress: 100,
          currentStep: 'Reprocessing completed successfully',
          pdfUrl: `${API_BASE_URL}/view-pdf/${reprocessResult.file_id}`,
          extractedText: reprocessResult.text_content || '',
          originalFilename: reprocessResult.original_filename || file.name,
          fileId: reprocessResult.file_id,
          aiOutput: reprocessResult.ai_output || undefined,
          aiPdfUrl: reprocessResult.ai_pdf_path ? `${API_BASE_URL}/view-ai-pdf/${reprocessResult.file_id}` : undefined
        };
        
        setFiles(prev => prev.map(f => 
          f.id === file.id ? updatedFile : f
        ));
        
        // Fetch complete CV data from database to get ai_generated_json
        console.log('Fetching complete CV data from database for reprocessed fileId:', reprocessResult.file_id);
        const cvData = await fetchCVDataFromDatabase(reprocessResult.file_id);
        if (cvData && cvData.aiGeneratedJson) {
          console.log('Found AI generated JSON in database for reprocessed file:', cvData.aiGeneratedJson);
          // Update the file with the complete data from database
          const updatedFileWithAI = {
            ...updatedFile,
            aiGeneratedJson: cvData.aiGeneratedJson
          };
          setFiles(prev => prev.map(f => 
            f.id === file.id ? updatedFileWithAI : f
          ));
          
          // Automatically select the completed file with AI data
          setSelectedFile(updatedFileWithAI);
        } else {
          // Automatically select the completed file
          setSelectedFile(updatedFile);
        }
        
      } else if (reprocessResult.file_id) {
        // Start progress tracking for the reprocessed file
        console.log('🔄 Starting progress tracking for reprocessed file');
        
        // Create a new progress tracking function for this specific file
        console.log('🔄 Starting progress tracking for reprocessed file ID:', reprocessResult.file_id);
        
        // Immediately fetch current progress to sync with backend
        const fetchCurrentReprocessProgress = async () => {
          try {
            const progressResponse = await fetch(`${API_BASE_URL}/cv/${reprocessResult.file_id}/progress`);
            if (progressResponse.ok) {
              const progressData = await progressResponse.json();
              if (progressData.success) {
                console.log('📊 Initial reprocess progress sync:', progressData);
                updateFileProgress(file.id, progressData.current_step, progressData.progress);
                
                // If processing is complete or failed, stop tracking
                if (progressData.status === 'completed' || progressData.status === 'error') {
                  updateFileProgress(file.id, progressData.current_step, progressData.progress, progressData.status);
                  return; // Don't start polling if already completed
                }
              }
            } else if (progressResponse.status === 404) {
              // File not found in progress tracking, might be completed
              console.log('⚠️ Progress tracking not found for reprocessed file, assuming completed');
              updateFileProgress(file.id, 'Processing completed', 100, 'completed');
              return; // Don't start polling if already completed
            }
          } catch (error) {
            console.error('Initial reprocess progress fetch error:', error);
          }
        };
        
        // Fetch current progress immediately
        fetchCurrentReprocessProgress();
        
        const reprocessProgressInterval = setInterval(async () => {
          try {
            const progressResponse = await fetch(`${API_BASE_URL}/cv/${reprocessResult.file_id}/progress`);
            if (progressResponse.ok) {
              const progressData = await progressResponse.json();
              if (progressData.success) {
                updateFileProgress(file.id, progressData.current_step, progressData.progress);
                
                // If processing is complete or failed, stop tracking
                if (progressData.status === 'completed' || progressData.status === 'error') {
                  updateFileProgress(file.id, progressData.current_step, progressData.progress, progressData.status);
                  removePollingInterval(file.id);
                  
                  // If completed, fetch complete AI data from database
                  if (progressData.status === 'completed') {
                    console.log('Fetching complete CV data from database for completed reprocessed fileId:', reprocessResult.file_id);
                    const cvData = await fetchCVDataFromDatabase(reprocessResult.file_id);
                    if (cvData && cvData.aiGeneratedJson) {
                      console.log('Found AI generated JSON in database for completed reprocessed file:', cvData.aiGeneratedJson);
                      // Update the file with the complete data from database
                      setFiles(prev => prev.map(f => 
                        f.id === file.id ? {
                          ...f,
                          aiGeneratedJson: cvData.aiGeneratedJson
                        } : f
                      ));
                    }
                  }
                }
              }
            } else if (progressResponse.status === 404) {
              // File not found in progress tracking, might be completed
              console.log('⚠️ Progress tracking not found for reprocessed file, assuming completed');
              updateFileProgress(file.id, 'Processing completed', 100, 'completed');
              removePollingInterval(file.id);
            }
          } catch (error) {
            console.error('Progress tracking error for reprocessed file:', error);
          }
        }, 1000); // Check progress every second
        
        // Add the interval to our tracking
        addPollingInterval(file.id, reprocessProgressInterval);
        
        // Update file status to processing
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'processing', 
            progress: 10,
            currentStep: 'Reprocessing file...'
          } : f
        ));
      }
      
      toast.success(`Existing file deleted. ${file.name} is now being reprocessed.`);
      
      // Close modal with more robust state reset
      console.log('✅ Closing duplicate modal after successful reprocess');
      console.log('Modal state before closing:', { duplicateModalOpen, hasDuplicateData: !!duplicateFileData });
      
      // Force modal to close by setting both states
      setDuplicateModalOpen(false);
      setDuplicateFileData(null);
      
      // Add a small delay to ensure state updates are processed
      setTimeout(() => {
        console.log('Modal state after closing (delayed):', { duplicateModalOpen: false, hasDuplicateData: false });
        // Force another state reset to ensure modal closes
        setDuplicateModalOpen(false);
        setDuplicateFileData(null);
      }, 100);
      
    } catch (error) {
      console.error('❌ Error during delete and reprocess:', error);
      const errorMessage = error instanceof Error ? error.message : 'Delete and reprocess failed';
      
      setFiles(prev => prev.map(f => 
        f.id === file.id ? {
          ...f,
          status: 'error',
          error: errorMessage,
          progress: 0,
          currentStep: 'Delete and reprocess failed'
        } : f
      ));

      toast.error(`Failed to delete and reprocess ${file.name}: ${errorMessage}`);
      
      // Close modal even on error with robust state reset
      console.log('❌ Closing duplicate modal after error');
      console.log('Modal state before closing (error):', { duplicateModalOpen, hasDuplicateData: !!duplicateFileData });
      
      // Force modal to close by setting both states
      setDuplicateModalOpen(false);
      setDuplicateFileData(null);
      
      // Add a small delay to ensure state updates are processed
      setTimeout(() => {
        console.log('Modal state after closing (error, delayed):', { duplicateModalOpen: false, hasDuplicateData: false });
        // Force another state reset to ensure modal closes
        setDuplicateModalOpen(false);
        setDuplicateFileData(null);
      }, 100);
    }
  };

  const handleDuplicateCancel = () => {
    if (!duplicateFileData) return;
    
    const { file } = duplicateFileData;
    
    // Remove the file from the list
    setFiles(prev => prev.filter(f => f.id !== file.id));
    
    toast.info(`Upload cancelled for ${file.name}`);
    
    // Close modal
    setDuplicateModalOpen(false);
    setDuplicateFileData(null);
  };

  // Function to fetch complete CV data from database
  const fetchCVDataFromDatabase = async (fileId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cv/${fileId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching CV data from database:', error);
      return null;
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    handleFiles(selectedFiles);
  };

  const handleFiles = (newFiles: File[]) => {
    const newUploads: UploadedFile[] = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0,
      currentStep: 'Starting upload...'
    }));

    setFiles(prev => [...prev, ...newUploads]);

    // Process each file with the backend API
    newUploads.forEach(file => {
      processFile(file, newFiles.find(f => f.name === file.name)!);
    });
  };

  const processFile = async (file: UploadedFile, originalFile: File) => {
    try {
      console.log('Starting to process file:', file.name);
      
      // Update status to processing
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { 
          ...f, 
          status: 'processing', 
          progress: 10,
          currentStep: 'File uploaded, starting processing...'
        } : f
      ));

      // Create FormData and upload to backend
      const formData = new FormData();
      formData.append('file', originalFile);
      
      console.log('FormData created, file size:', originalFile.size);
      console.log('Uploading to:', `${API_BASE_URL}/upload-cv`);

      // Start real-time progress tracking
      let fileId: string | null = null;
      
      const startProgressTracking = (id: string) => {
        fileId = id;
        console.log('🔄 Starting progress tracking for file ID:', id);
        
        // Immediately fetch current progress to sync with backend
        const fetchCurrentProgress = async () => {
          try {
            const progressResponse = await fetch(`${API_BASE_URL}/cv/${id}/progress`);
            if (progressResponse.ok) {
              const progressData = await progressResponse.json();
              if (progressData.success) {
                console.log('📊 Initial progress sync:', progressData);
                updateFileProgress(file.id, progressData.current_step, progressData.progress);
                
                // If processing is complete or failed, stop tracking
                if (progressData.status === 'completed' || progressData.status === 'error') {
                  updateFileProgress(file.id, progressData.current_step, progressData.progress, progressData.status);
                  return; // Don't start polling if already completed
                }
              }
            } else if (progressResponse.status === 404) {
              // File not found in progress tracking, might be completed
              console.log('⚠️ Progress tracking not found for file, assuming completed');
              updateFileProgress(file.id, 'Processing completed', 100, 'completed');
              return; // Don't start polling if already completed
            }
          } catch (error) {
            console.error('Initial progress fetch error:', error);
          }
        };
        
        // Fetch current progress immediately
        fetchCurrentProgress();
        
        const progressInterval = setInterval(async () => {
          try {
            const progressResponse = await fetch(`${API_BASE_URL}/cv/${id}/progress`);
            if (progressResponse.ok) {
              const progressData = await progressResponse.json();
              if (progressData.success) {
                updateFileProgress(file.id, progressData.current_step, progressData.progress);
                
                // If processing is complete or failed, stop tracking
                if (progressData.status === 'completed' || progressData.status === 'error') {
                  updateFileProgress(file.id, progressData.current_step, progressData.progress, progressData.status);
                  removePollingInterval(file.id);
                  
                  // If completed, fetch complete AI data from database
                  if (progressData.status === 'completed') {
                    console.log('Fetching complete CV data from database for completed fileId:', id);
                    const cvData = await fetchCVDataFromDatabase(id);
                    if (cvData && cvData.aiGeneratedJson) {
                      console.log('Found AI generated JSON in database for completed file:', cvData.aiGeneratedJson);
                      // Update the file with the complete data from database
                      setFiles(prev => prev.map(f => 
                        f.id === file.id ? {
                          ...f,
                          aiGeneratedJson: cvData.aiGeneratedJson
                        } : f
                      ));
                    }
                  }
                }
              }
            } else if (progressResponse.status === 404) {
              // File not found in progress tracking, might be completed
              console.log('⚠️ Progress tracking not found for file, assuming completed');
              updateFileProgress(file.id, 'Processing completed', 100, 'completed');
              removePollingInterval(file.id);
            }
          } catch (error) {
            console.error('Progress tracking error:', error);
            // Don't stop tracking on network errors, just log them
          }
        }, 1000); // Check progress every second
        
        // Add the interval to our tracking
        addPollingInterval(file.id, progressInterval);
      };

      const response = await fetch(`${API_BASE_URL}/upload-cv`, {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        let errorMessage = 'Upload failed';
        let errorDetails = '';
        
        try {
          const errorData = await response.json();
          console.error('Error response:', errorData);
          errorMessage = errorData.detail || errorData.message || 'Upload failed';
          
          // Check if this is an OCR-related error
          if (errorMessage.includes('OCR') || errorMessage.includes('image-based')) {
            errorDetails = getOCRErrorDetails(errorMessage);
          }
        } catch (parseError) {
          console.error('Could not parse error response:', parseError);
          errorMessage = `Upload failed with status ${response.status}`;
        }
        
        // If we have OCR error details, include them
        if (errorDetails) {
          errorMessage = `${errorMessage}\n\n${errorDetails}`;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Success response:', result);
      console.log('AI output available:', !!result.ai_output);
      console.log('AI PDF path:', result.ai_pdf_path);
      console.log('Text content length:', result.text_content?.length || 0);
      console.log('Is duplicate:', result.is_duplicate);
      console.log('Duplicate file ID:', result.duplicate_file_id);

      // Validate the response
      if (!result.file_id) {
        throw new Error('Backend did not return a file ID');
      }

      // Check if this is a duplicate file
      if (result.is_duplicate) {
        console.log('📋 Duplicate file detected, asking user for action');
        console.log('🔍 Duplicate details:', {
          file_name: file.name,
          duplicate_file_id: result.duplicate_file_id,
          duplicate_filename: result.duplicate_filename
        });
        
        // Show toast notification about duplicate detection
        toast.warning(`Duplicate file detected: ${file.name}`, {
          description: "Please choose whether to delete existing file and reupload, or cancel.",
          duration: 5,
        });
        
        // Set up modal data and show modal
        setDuplicateFileData({
          file,
          originalFile,
          duplicateFileId: result.duplicate_file_id,
          duplicateFilename: result.duplicate_filename
        });
        setDuplicateModalOpen(true);
        
        return; // Exit early, modal will handle the rest
      }

      // Check if processing completed immediately
      if (result.success && result.processing_status === 'completed') {
        console.log('✅ Upload processing completed immediately');
        
        // Update file status to completed
        const updatedFile = {
          ...file,
          status: 'completed' as const,
          progress: 100,
          currentStep: 'Processing completed successfully',
          pdfUrl: `${API_BASE_URL}/view-pdf/${result.file_id}`,
          extractedText: result.text_content || '',
          originalFilename: result.original_filename || file.name,
          fileId: result.file_id,
          aiOutput: result.ai_output || undefined,
          aiPdfUrl: result.ai_pdf_path ? `${API_BASE_URL}/view-ai-pdf/${result.file_id}` : undefined
        };
        
        setFiles(prev => prev.map(f => 
          f.id === file.id ? updatedFile : f
        ));
        
        // Fetch complete CV data from database to get ai_generated_json
        console.log('Fetching complete CV data from database for uploaded fileId:', result.file_id);
        const cvData = await fetchCVDataFromDatabase(result.file_id);
        if (cvData && cvData.aiGeneratedJson) {
          console.log('Found AI generated JSON in database for uploaded file:', cvData.aiGeneratedJson);
          // Update the file with the complete data from database
          const updatedFileWithAI = {
            ...updatedFile,
            aiGeneratedJson: cvData.aiGeneratedJson
          };
          setFiles(prev => prev.map(f => 
            f.id === file.id ? updatedFileWithAI : f
          ));
          
          // Automatically select the completed file with AI data
          setSelectedFile(updatedFileWithAI);
        } else {
          // Automatically select the completed file
          setSelectedFile(updatedFile);
        }
        
        toast.success(`${file.name} processed successfully!`);
        
      } else if (result.file_id) {
        // Start progress tracking if we have a file ID and it's not completed
        console.log('🔄 Starting progress tracking for uploaded file');
        startProgressTracking(result.file_id);
        
        // For files that are still processing, we'll let the progress tracking handle the completion
        // The progress tracking will update the file status when it completes
      }
    } catch (error) {
      console.error('Error processing file:', error);
      const errorMessage = error instanceof Error ? error.message : 'Processing failed';
      
      setFiles(prev => prev.map(f => 
        f.id === file.id ? {
          ...f,
          status: 'error',
          error: errorMessage,
          progress: 0,
          currentStep: 'Processing failed'
        } : f
      ));

      // Show appropriate toast message based on error type
      if (errorMessage.includes('OCR') || errorMessage.includes('image-based')) {
        toast.error(`OCR Required: ${file.name} appears to be image-based`, {
          description: "This document needs OCR to extract text. Check the error details below.",
          duration: 8000,
        });
      } else {
        toast.error(`Failed to process ${file.name}: ${errorMessage}`);
      }
    }
  };

  // Function to update file progress based on backend workflow steps
  const updateFileProgress = (fileId: string, step: string, progress: number, status?: string) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { 
        ...f, 
        currentStep: step,
        progress: progress,
        ...(status && { status: status as 'uploading' | 'processing' | 'completed' | 'error' })
      } : f
    ));
  };

  const getOCRErrorDetails = (errorMessage: string): string => {
    if (errorMessage.includes('OCR is not available') || errorMessage.includes('install Tesseract')) {
      return `🔧 To fix this issue:

1. Install Tesseract OCR on your system:
   • Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   • macOS: brew install tesseract
   • Ubuntu: sudo apt-get install tesseract-ocr

2. Restart the application
3. Try uploading your document again

💡 Tesseract OCR will enable text extraction from image-based PDFs and scanned documents.`;
    } else if (errorMessage.includes('OCR extraction failed') || errorMessage.includes('image quality')) {
      return `📸 Possible solutions for image-based documents:

1. Ensure the document images are clear and high quality
2. Check if the document has security restrictions
3. Try a different document with better image quality
4. Make sure the text in the images is readable and not too small

💡 OCR works best with clear, high-resolution images containing readable text.`;
    } else if (errorMessage.includes('image-based')) {
      return `🖼️ This document appears to be image-based (scanned or contains only images).

To extract text from images, you need:
1. Tesseract OCR installed on your system
2. Clear, readable images
3. Good image quality (300+ DPI recommended)

💡 Consider using the original document file (DOCX, PDF) instead of scanned versions.`;
    }
    
    return '';
  };

  const selectFile = async (file: UploadedFile) => {
    if (file.status === 'completed') {
      setSelectedFile(file);
      // Reset view mode to extracted_text when selecting a new file
      setCurrentViewMode('extracted_text');
      // Clear any previous JSON errors
      setJsonErrorDetails(null);
      // Reset PDF error state
      setPdfLoadError(false);
      console.log('Selected file:', file.name);
      console.log('File has extracted text:', !!file.extractedText);
      console.log('File has AI output:', !!file.aiOutput);
      console.log('File has AI PDF:', !!file.aiPdfUrl);
      
      // Fetch complete CV data from database if we have a fileId
      if (file.fileId) {
        console.log('Fetching complete CV data from database for fileId:', file.fileId);
        const cvData = await fetchCVDataFromDatabase(file.fileId);
        if (cvData && cvData.aiGeneratedJson) {
          console.log('Found AI generated JSON in database:', cvData.aiGeneratedJson);
          // Update the file with the complete data from database
          const updatedFile = {
            ...file,
            aiGeneratedJson: cvData.aiGeneratedJson
          };
          setSelectedFile(updatedFile);
          
          // Also update the file in the files array
          setFiles(prev => prev.map(f => 
            f.id === file.id ? updatedFile : f
          ));
        }
      }
    }
  };

  // Debug effect for selected file
  useEffect(() => {
    if (selectedFile) {
      console.log('Selected file changed:', selectedFile);
      console.log('File status:', selectedFile.status);
      console.log('File PDF URL:', selectedFile.pdfUrl);
      console.log('File extracted text length:', selectedFile.extractedText?.length || 0);
      
      // Additional debug info for display rendering
      if (selectedFile.status === 'completed') {
        console.log('✅ File is completed, should display PDF and text');
        console.log('PDF URL for iframe:', selectedFile.pdfUrl);
        console.log('Text content preview:', selectedFile.extractedText?.substring(0, 100) + '...');
      }
    }
  }, [selectedFile]);

  // Debug effect for files array changes
  useEffect(() => {
    console.log('Files array changed:', files);
    console.log('Files with completed status:', files.filter(f => f.status === 'completed'));
  }, [files]);

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    if (selectedFile?.id === fileId) {
      setSelectedFile(null);
    }
  };

  const resetAllFiles = () => {
    setFiles([]);
    setSelectedFile(null);
    setJsonErrorDetails(null);
    setCurrentJsonFile(null);
    setCurrentViewMode('extracted_text');
    // Reset file input values to allow re-uploading the same files
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach((input) => {
      (input as HTMLInputElement).value = '';
    });
  };

  const downloadFile = async (file: UploadedFile) => {
    try {
      if (!file.pdfUrl) {
        toast.error('No PDF available for download');
        return;
      }

      const response = await fetch(file.pdfUrl);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${file.originalFilename || file.name.replace(/\.[^/.]+$/, '')}_converted.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('PDF downloaded successfully!');
    } catch (err) {
      toast.error('Download failed');
    }
  };

  const downloadAIPdf = async (file: UploadedFile) => {
    try {
      if (!file.aiPdfUrl) {
        toast.error('No AI-generated PDF available for download');
        return;
      }

      const response = await fetch(file.aiPdfUrl);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${file.originalFilename || file.name.replace(/\.[^/.]+$/, '')}_ai_generated.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('AI-generated PDF downloaded successfully!');
    } catch (err) {
      toast.error('Download failed');
    }
  };

  const processJsonFile = async (file: UploadedFile) => {
    try {
      // Set current file and clear previous errors
      setCurrentJsonFile(file);
      setJsonErrorDetails(null);
      setIsProcessingJson(true);
      
      // Extract file_id from the URL
      const fileId = file.pdfUrl?.split('/').pop();
      if (!fileId) {
        toast.error('File not available for JSON processing');
        return;
      }

      toast.info('Processing file for JSON extraction...');
      
      const response = await fetch(`${API_BASE_URL}/process-json/${fileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.originalFilename || file.name,
          extracted_text: file.extractedText || ''
        })
      });

      const result = await response.json();
      
      // Check if this is an error response
      if (result.error) {
        setJsonErrorDetails(result);
        toast.error('JSON processing failed - check details below');
        return;
      }

      if (!response.ok) {
        throw new Error('JSON processing failed');
      }
      
      // Store the AI output in the file
      const updatedFile = { ...file, aiOutput: result };
      setFiles(prev => prev.map(f => f.id === file.id ? updatedFile : f));
      
      // Update selected file if it's the current one
      if (selectedFile?.id === file.id) {
        setSelectedFile(updatedFile);
      }
      
      toast.success('JSON extraction completed successfully!');
      setCurrentJsonFile(null);
      
      // Automatically switch to JSON view mode
      setCurrentViewMode('json_output');
      
    } catch (error) {
      console.error('JSON processing error:', error);
      toast.error('JSON processing failed');
      setCurrentJsonFile(null);
    } finally {
      setIsProcessingJson(false);
    }
  };

  const generateAIPdf = async (file: UploadedFile) => {
    try {
      if (!file.aiGeneratedJson) {
        toast.error('No AI generated profile data available. Please wait for processing to complete.');
        return;
      }

      setIsGeneratingPdf(true);
      
      // Use fileId directly if available, otherwise extract from URL
      const fileId = file.fileId || file.pdfUrl?.split('/').pop();
      if (!fileId) {
        toast.error('File not available for PDF generation');
        return;
      }

      toast.info('Generating PDF from AI profile data...');
      
      // Use the new profile PDF generation endpoint
      const response = await fetch(`${API_BASE_URL}/generate-profile-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileId: fileId,
          profileData: file.aiGeneratedJson,
          originalFilename: file.originalFilename || file.name
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'PDF generation failed');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${file.originalFilename || file.name}_profile.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Profile PDF generated successfully!');
      
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('PDF generation failed');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const retryJsonProcessing = async () => {
    if (currentJsonFile) {
      await processJsonFile(currentJsonFile);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />;
      case 'processing':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: UploadedFile['status']) => {
    const variants = {
      uploading: 'bg-blue-100 text-blue-800',
      processing: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      error: 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <PageWrapper className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        {/* Back to Dashboard Button */}
        <PageSection index={0}>
          <div className="flex items-center gap-4 mb-4">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </PageSection>
        
        <PageSection index={1}>
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold">CV Document Upload & Conversion</h1>
            <p className="text-muted-foreground">
              Upload CV documents and convert them to PDF with text extraction
            </p>
          </div>
        </PageSection>

        {/* Initial Screen: Upload Section and How It Works Side by Side */}
        {files.length === 0 ? (
          <PageSection index={2}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upload Section - Left Side */}
              <Card>
                <CardHeader>
                  <CardTitle>Upload CV Documents</CardTitle>
                  <CardDescription>
                    Drag and drop your CV files here or click to browse. All documents will be converted to PDF.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      dragActive 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-lg font-medium text-gray-900 mb-2">
                      Drop your CV files here
                    </p>
                    <p className="text-sm text-gray-500 mb-4">
                      or click to browse files
                    </p>
                    <Button onClick={() => document.getElementById('file-input')?.click()}>
                      Choose Files
                    </Button>
                    <input
                      id="file-input"
                      type="file"
                      multiple
                      accept=".pdf,.docx,.doc,.txt,.rtf,.jpg,.jpeg,.png,.bmp,.tiff"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </div>

                  {/* Supported Formats Info */}
                  <div className="mt-4 text-sm text-muted-foreground">
                    <p className="font-medium mb-2">Supported input formats:</p>
                    <div className="flex flex-wrap gap-2">
                      {['PDF', 'DOCX', 'DOC', 'TXT', 'RTF', 'JPG', 'JPEG', 'PNG', 'BMP', 'TIFF'].map(format => (
                        <Badge key={format} variant="secondary" className="text-xs">
                          {format}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* How It Works - Right Side */}
              <Card>
                <CardHeader>
                  <CardTitle>How it works</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="bg-blue-100 rounded-full p-2 mt-0.5">
                      <Upload className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium">Upload</p>
                      <p className="text-sm text-muted-foreground">Drag and drop your CV documents</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="bg-green-100 rounded-full p-2 mt-0.5">
                      <FileText className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">Convert</p>
                      <p className="text-sm text-muted-foreground">Documents are automatically converted to PDF</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="bg-purple-100 rounded-full p-2 mt-0.5">
                      <Download className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium">Download</p>
                      <p className="text-sm text-muted-foreground">Get your converted PDF files</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </PageSection>
        ) : (
          <PageSection index={2}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-6">
              {/* Upload Section - Left Side */}
              <Card>
                <CardHeader>
                  <CardTitle>Upload More CV Documents</CardTitle>
                  <CardDescription>
                    Drag and drop additional CV files here or click to browse. All documents will be converted to PDF.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      dragActive 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-lg font-medium text-gray-900 mb-2">
                      Drop your CV files here
                    </p>
                    <p className="text-sm text-gray-500 mb-4">
                      or click to browse files
                    </p>
                    <Button onClick={() => document.getElementById('file-input')?.click()}>
                      Choose Files
                    </Button>
                    <input
                      id="file-input"
                      type="file"
                      multiple
                      accept=".pdf,.docx,.doc,.txt,.rtf,.jpg,.jpeg,.png,.bmp,.tiff"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* File List - Right Side */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Uploaded Files</CardTitle>
                      <CardDescription>
                        {files.length} file{files.length !== 1 ? 's' : ''} uploaded
                      </CardDescription>
                    </div>
                    <Button
                      onClick={resetAllFiles}
                      size="sm"
                      variant="secondary"
                      className="h-8 bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300"
                    >
                      Reset All Files
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {files.map((file) => (
                      <div
                        key={file.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedFile?.id === file.id 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => file.status === 'completed' && selectFile(file)}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0 mt-1">
                            <FileText className="h-4 w-4 text-gray-400" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-2">
                              <p className="font-medium text-sm truncate">{file.name}</p>
                              <div className="flex items-center space-x-2">
                                {getStatusIcon(file.status)}
                                {getStatusBadge(file.status)}
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              <p className="text-xs text-muted-foreground">
                                {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type}
                              </p>
                              
                              {/* Processing Step Display */}
                              {file.status === 'uploading' && (
                                <div className="text-xs text-blue-600">
                                  📤 Uploading file...
                                </div>
                              )}
                              
                              {file.status === 'processing' && (
                                <div className="text-xs text-yellow-600">
                                  🔄 {file.currentStep || 'Processing...'}
                                </div>
                              )}
                              
                              {file.status === 'completed' && (
                                <div className="text-xs text-green-600">
                                  ✅ {file.currentStep || 'Processing completed'}
                                </div>
                              )}
                              
                              {file.status === 'error' && (
                                <div className="text-xs text-red-600">
                                  ❌ {file.error || 'Processing failed'}
                                </div>
                              )}
                              
                              {/* Progress Bar */}
                              {file.status === 'uploading' && (
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className="h-full bg-blue-500 rounded-full transition-all duration-300"
                                    style={{ width: `${file.progress}%` }}
                                  />
                                </div>
                              )}
                              
                              {file.status === 'processing' && (
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className="h-full bg-yellow-500 rounded-full transition-all duration-300"
                                    style={{ width: `${file.progress || 50}%` }}
                                  />
                                </div>
                              )}
                              
                              {/* Progress Percentage */}
                              {file.status === 'processing' && (
                                <div className="text-xs text-gray-500 text-right">
                                  {file.progress}% complete
                                </div>
                              )}

                              {/* AI Model Information */}
                              {file.status === 'completed' && file.aiOutput && (
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                  <span className="icon">🤖</span>
                                  <span>AI Model: {file.aiOutput.model_used || 'OpenRouter AI'}</span>
                                </div>
                              )}
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex items-center space-x-2 mt-3">
                              {file.status === 'completed' && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="h-7 px-2 text-xs"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadFile(file);
                                    }}
                                  >
                                    <Download className="h-3 w-3 mr-1" />
                                    Download
                                  </Button>
                                  {file.aiPdfUrl && (
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      className="h-7 px-2 text-xs"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        downloadAIPdf(file);
                                      }}
                                    >
                                      <Download className="h-3 w-3 mr-1" />
                                      AI PDF
                                    </Button>
                                  )}
                                </>
                              )}

                              {/* Stop Button for Processing Files */}
                              {file.status === 'processing' && (
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  className="h-7 px-2 text-xs"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    stopFileProcessing(file.id);
                                  }}
                                >
                                  <Square className="h-3 w-3 mr-1" />
                                  Stop
                                </Button>
                              )}

                              <Button
                                size="sm"
                                variant="outline"
                                className="h-7 px-2 text-xs"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  processJsonFile(file);
                                }}
                                disabled={isProcessingJson}
                              >
                                {isProcessingJson && currentJsonFile?.id === file.id ? (
                                  <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                ) : (
                                  <FileJson className="h-3 w-3 mr-1" />
                                )}
                                {isProcessingJson && currentJsonFile?.id === file.id ? 'Processing...' : 'Json'}
                              </Button>

                              {file.aiGeneratedJson && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-7 px-2 text-xs"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    generateAIPdf(file);
                                  }}
                                  disabled={isGeneratingPdf}
                                >
                                  {isGeneratingPdf ? (
                                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                  ) : (
                                    <FileText className="h-3 w-3 mr-1" />
                                  )}
                                  {isGeneratingPdf ? 'Generating...' : 'Profile'}
                                </Button>
                              )}

                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-7 px-2 text-xs"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeFile(file.id);
                                }}
                              >
                                Remove
                              </Button>
                            </div>

                            {/* Error Details */}
                            {file.status === 'error' && file.error && (
                              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                                <div className="flex items-start space-x-2">
                                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                                  <div className="flex-1">
                                    <p className="text-sm font-medium text-red-800 mb-1">Processing Error</p>
                                    <p className="text-xs text-red-700 whitespace-pre-line">{file.error}</p>
                                    
                                    {/* Show OCR-specific help */}
                                    {file.error.includes('OCR') && (
                                      <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                                        <p className="text-xs font-medium text-blue-800 mb-1">💡 Need help with OCR?</p>
                                        <p className="text-xs text-blue-700">
                                          This document appears to be image-based. Check the error details above for installation instructions.
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            {/* JSON Error Display Section */}
            {jsonErrorDetails && (
              <Card className="border-red-200 bg-red-50">
                <CardHeader>
                  <CardTitle className="text-red-800 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    JSON Processing Error
                  </CardTitle>
                  <CardDescription className="text-red-700">
                    Failed to process {jsonErrorDetails.filename || 'file'} for JSON extraction
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-white p-3 rounded border border-red-200">
                    <h4 className="font-medium text-red-800 mb-2">Error Details:</h4>
                    <p className="text-sm text-red-700">{jsonErrorDetails.error_message}</p>
                  </div>
                  
                  {jsonErrorDetails.text_content_preview && (
                    <div className="bg-white p-3 rounded border border-red-200">
                      <h4 className="font-medium text-red-800 mb-2">Text Content Preview:</h4>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap max-h-32 overflow-auto">
                        {jsonErrorDetails.text_content_preview}
                      </p>
                    </div>
                  )}
                  
                  {jsonErrorDetails.raw_ai_response && (
                    <div className="bg-white p-3 rounded border border-red-200">
                      <h4 className="font-medium text-red-800 mb-2">Raw AI Response:</h4>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap max-h-32 overflow-auto font-mono">
                        {jsonErrorDetails.raw_ai_response}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    {jsonErrorDetails.can_retry && (
                      <Button 
                        onClick={retryJsonProcessing}
                        disabled={isProcessingJson}
                        className="bg-red-600 hover:bg-red-700"
                      >
                        {isProcessingJson ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Retrying...
                          </>
                        ) : (
                          'Retry Processing'
                        )}
                      </Button>
                    )}
                    <Button 
                      variant="outline"
                      onClick={() => setJsonErrorDetails(null)}
                    >
                      Dismiss
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

          </div>



          {/* Selected File Details - Full Width Below Grid */}
          {selectedFile && (
                <Card>
                  <CardHeader>
                    <CardTitle>File Details: {selectedFile.name}</CardTitle>
                    <CardDescription>
                      Status: {selectedFile.status} | Progress: {selectedFile.progress}%
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Progress Bar */}
                      {selectedFile.status === 'processing' && (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Processing...</span>
                            <span>{selectedFile.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${selectedFile.progress}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500">{selectedFile.currentStep}</p>
                        </div>
                      )}

                      {/* Error Display */}
                      {selectedFile.status === 'error' && selectedFile.error && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <AlertCircle className="h-5 w-5 text-red-600" />
                            <span className="font-medium text-red-800">Processing Error</span>
                          </div>
                          <p className="text-sm text-red-700 mb-3">{selectedFile.error}</p>
                          
                          {/* OCR Error Details */}
                          {getOCRErrorDetails(selectedFile.error) && (
                            <div className="mt-3 p-3 bg-white border border-red-200 rounded text-sm text-red-700 whitespace-pre-line">
                              {getOCRErrorDetails(selectedFile.error)}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Success Display */}
                      {selectedFile.status === 'completed' && (
                        <div className="space-y-4">
                          {/* Success Message */}
                          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-center space-x-2">
                              <CheckCircle className="h-5 w-5 text-green-600" />
                              <span className="font-medium text-green-800">Processing Completed Successfully!</span>
                            </div>
                          </div>

                          {/* AI Model Information */}
                          {selectedFile.aiOutput && (
                            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                              <div className="flex items-center space-x-2">
                                <span className="text-2xl">🤖</span>
                                <div>
                                  <p className="font-medium text-blue-800">
                                    AI Model: {selectedFile.aiOutput.model_used || 'OpenRouter AI'}
                                  </p>
                                  {selectedFile.aiOutput.processing_duration_ms && (
                                    <p className="text-sm text-blue-600">
                                      Processing time: {Math.round(selectedFile.aiOutput.processing_duration_ms / 1000)} seconds
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Two Column Layout: PDF on Left, Content on Right */}
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Left Side - Converted PDF */}
                            <div className="space-y-4">
                              <h3 className="font-medium text-lg">Converted PDF</h3>
                              {selectedFile.pdfUrl ? (
                                <div className="border rounded-lg p-4 bg-gray-50">
                                  <div className="bg-white rounded border h-170 overflow-hidden">
                                    {!pdfLoadError ? (
                                      <iframe
                                        src={selectedFile.pdfUrl}
                                        className="w-full h-full"
                                        title="Converted PDF Viewer"
                                        onError={() => {
                                          console.error('PDF iframe failed to load');
                                          setPdfLoadError(true);
                                        }}
                                        onLoad={() => {
                                          console.log('PDF iframe loaded successfully');
                                          setPdfLoadError(false);
                                        }}
                                      />
                                    ) : (
                                      <div className="h-full flex items-center justify-center">
                                        <div className="text-center space-y-2">
                                          <FileText className="h-8 w-8 mx-auto text-gray-400" />
                                          <p className="text-sm text-gray-600">PDF Viewer</p>
                                          <p className="text-xs text-gray-500">PDF failed to load</p>
                                          <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => setPdfLoadError(false)}
                                          >
                                            Retry
                                          </Button>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                  <div className="text-center text-gray-500 text-xs p-2 bg-gray-50 border-t">
                                    If PDF doesn't display, use the buttons below
                                  </div>
                                  <div className="flex gap-2 mt-3">
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      className="gap-2"
                                      onClick={() => {
                                        try {
                                          console.log('Attempting to open PDF:', selectedFile.pdfUrl);
                                          window.open(selectedFile.pdfUrl, '_blank');
                                        } catch (error) {
                                          console.error('Error opening PDF:', error);
                                          toast.error('Failed to open PDF. Please try downloading instead.');
                                        }
                                      }}
                                    >
                                      <Download className="h-4 w-4" />
                                      Open PDF in New Tab
                                    </Button>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      className="gap-2"
                                      onClick={() => downloadFile(selectedFile)}
                                    >
                                      <Download className="h-4 w-4" />
                                      Download PDF
                                    </Button>
                                  </div>
                                  <div className="text-xs text-gray-500 mt-2">
                                    <p><strong>File ID:</strong> {selectedFile.pdfUrl?.split('/').pop()}</p>
                                    <p><strong>Note:</strong> If PDF viewing fails, try downloading instead</p>
                                  </div>
                                </div>
                              ) : (
                                <div className="text-center py-8 text-gray-500 border rounded-lg">
                                  <FileText className="mx-auto h-12 w-12 mb-2" />
                                  <p>No PDF Available</p>
                                  <p className="text-sm">PDF conversion is in progress or failed</p>
                                </div>
                              )}
                            </div>

                            {/* Right Side - Toggle Content */}
                            <div className="space-y-4">
                              <h3 className="font-medium text-lg">Content Options</h3>
                              
                              {/* Toggle Buttons */}
                              <div className="flex flex-row gap-2">
                                <Button
                                  variant={currentViewMode === 'extracted_text' ? 'default' : 'outline'}
                                  className="flex-1 justify-center gap-2 h-10 text-sm"
                                  onClick={() => setCurrentViewMode('extracted_text')}
                                >
                                  <FileText className="h-4 w-4" />
                                  <span>Extracted Text</span>
                                </Button>

                                <Button
                                  variant={currentViewMode === 'json_output' ? 'default' : 'outline'}
                                  className="flex-1 justify-center gap-2 h-10 text-sm"
                                  onClick={() => setCurrentViewMode('json_output')}
                                >
                                  <FileJson className="h-4 w-4" />
                                  <span>AI Output (JSON)</span>
                                </Button>

                                <Button
                                  variant={currentViewMode === 'ai_pdf' ? 'default' : 'outline'}
                                  className="flex-1 justify-center gap-2 h-10 text-sm"
                                  onClick={() => setCurrentViewMode('ai_pdf')}
                                >
                                  <FileText className="h-4 w-4" />
                                  <span>AI Generated Profile Data</span>
                                </Button>
                              </div>

                              {/* Content Display */}
                              <div className="border rounded-lg p-4 min-h-96">
                                {currentViewMode === 'extracted_text' && (
                                  <div>
                                    <h4 className="font-medium mb-3">Extracted Text Content</h4>
                                    <div className="bg-gray-50 p-3 rounded text-sm max-h-140 overflow-y-auto">
                                      {selectedFile.extractedText || 'No text content available'}
                                    </div>
                                  </div>
                                )}

                                {currentViewMode === 'json_output' && (
                                  <div>
                                    <h4 className="font-medium mb-3">AI Generated JSON Output</h4>
                                    {selectedFile.aiGeneratedJson ? (
                                      <div className="space-y-3">
                                        <div className="bg-gray-50 p-3 rounded text-sm max-h-140 overflow-y-auto">
                                          <pre className="whitespace-pre-wrap">
                                            {JSON.stringify(selectedFile.aiGeneratedJson, null, 2)}
                                          </pre>
                                        </div>
                                        <Button
                                          variant="outline"
                                          size="sm"
                                          className="gap-2"
                                          onClick={() => {
                                            const blob = new Blob([JSON.stringify(selectedFile.aiGeneratedJson, null, 2)], {
                                              type: 'application/json'
                                            });
                                            const url = URL.createObjectURL(blob);
                                            const a = document.createElement('a');
                                            a.href = url;
                                            a.download = `${selectedFile.originalFilename || selectedFile.name}_ai_output.json`;
                                            document.body.appendChild(a);
                                            a.click();
                                            document.body.removeChild(a);
                                            URL.revokeObjectURL(url);
                                          }}
                                        >
                                          <Download className="h-4 w-4" />
                                          Download JSON
                                        </Button>
                                      </div>
                                    ) : (
                                      <div className="text-center py-8 text-gray-500">
                                        <FileJson className="mx-auto h-12 w-12 mb-2" />
                                        <p>AI Output Processing</p>
                                        <p className="text-sm">The AI is currently processing your document to extract structured information.</p>
                                      </div>
                                    )}
                                  </div>
                                )}

                                {currentViewMode === 'ai_pdf' && (
                                  <div>
                                    <h4 className="font-medium mb-3">AI Generated Profile Data</h4>
                                    {selectedFile.aiGeneratedJson ? (
                                      <div className="space-y-3">
                                        <div className="bg-white p-4 rounded border max-h-140 overflow-y-auto">
                                          <StructuredJSONViewer data={selectedFile.aiGeneratedJson} />
                                        </div>
                                        <Button
                                          variant="outline"
                                          size="sm"
                                          className="gap-2"
                                          onClick={() => {
                                            const blob = new Blob([JSON.stringify(selectedFile.aiGeneratedJson, null, 2)], {
                                              type: 'application/json'
                                            });
                                            const url = URL.createObjectURL(blob);
                                            const a = document.createElement('a');
                                            a.href = url;
                                            a.download = `${selectedFile.originalFilename || selectedFile.name}_profile_data.json`;
                                            document.body.appendChild(a);
                                            a.click();
                                            document.body.removeChild(a);
                                            URL.revokeObjectURL(url);
                                          }}
                                        >
                                          <Download className="h-4 w-4" />
                                          Download Profile Data
                                        </Button>
                                      </div>
                                    ) : (
                                      <div className="text-center py-8 text-gray-500">
                                        <FileText className="mx-auto h-12 w-12 mb-2" />
                                        <p>AI Profile Data Processing</p>
                                        <p className="text-sm">The AI is currently processing your document to extract structured profile information.</p>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
          </PageSection>
        )}
      </PageWrapper>

      {/* Duplicate File Modal */}
      <Dialog 
        key={`duplicate-modal-${duplicateModalOpen}-${duplicateFileData?.file.id || 'none'}`}
        open={duplicateModalOpen} 
        onOpenChange={(open) => {
          console.log('Dialog onOpenChange called with:', open);
          setDuplicateModalOpen(open);
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Duplicate File Detected
            </DialogTitle>
            <DialogDescription>
              File "{duplicateFileData?.file.name}" already exists in the database.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <p className="font-medium mb-1">What would you like to do?</p>
                  <ul className="space-y-1 text-xs">
                    <li>• <strong>Delete and Reupload:</strong> Remove the existing file and process the new one</li>
                    <li>• <strong>Cancel:</strong> Keep the existing file and cancel this upload</li>
                  </ul>
                  <p className="mt-2 text-xs font-medium text-red-600">
                    ⚠️ Warning: Deleting will permanently remove the existing file and all its data.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={handleDuplicateCancel}
              className="flex items-center gap-2"
            >
              <X className="h-4 w-4" />
              Cancel Upload
            </Button>
            <Button
              onClick={handleDuplicateDeleteAndReupload}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700"
            >
              <Trash2 className="h-4 w-4" />
              Delete & Reupload
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CVUploadPage;
