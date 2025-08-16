import React, { useState, useRef } from 'react';
import { Upload, FileText, Download, Trash2, Loader2, RotateCcw } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';

interface UploadResponse {
  success: boolean;
  file_id: string;
  original_filename: string;
  pdf_path: string;
  text_content: string;
  file_type: string;
}

const CVUpload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = 'http://localhost:8000';

  const resetState = () => {
    setUploadedFile(null);
    setError(null);
    setIsUploading(false);
    // Reset the file input value to allow re-uploading the same file
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/rtf',
      'text/plain',
      'application/json',
      'image/jpeg',
      'image/png',
      'image/bmp',
      'image/tiff'
    ];

    if (!allowedTypes.includes(file.type)) {
      setError('File type not supported. Please upload PDF, DOC, DOCX, RTF, TXT, JSON, or image files.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload-cv`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result: UploadResponse = await response.json();
      
      // Validate the response
      if (!result.text_content || result.text_content.trim() === '') {
        throw new Error('Document processing failed - no text content was extracted. Please try a different file.');
      }
      
      setUploadedFile(result);
      toast.success('Document uploaded and processed successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      toast.error('Upload failed: ' + errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!uploadedFile) return;

    try {
      const response = await fetch(`${API_BASE_URL}/download-pdf/${uploadedFile.file_id}`);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${uploadedFile.original_filename.replace(/\.[^/.]+$/, '')}_converted.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('PDF downloaded successfully!');
    } catch (err) {
      toast.error('Download failed');
    }
  };

  const handleDeleteDocument = async () => {
    if (!uploadedFile) return;

    try {
      const response = await fetch(`${API_BASE_URL}/document/${uploadedFile.file_id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Delete failed');

      resetState();
      toast.success('Document deleted successfully!');
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            CV Document Upload & Processing
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium mb-2">Upload your CV document</p>
              <p className="text-sm text-gray-500 mb-4">
                Supports PDF, DOC, DOCX, RTF, TXT, JSON, and image files (JPG, PNG, BMP, TIFF)
              </p>
              <div className="flex gap-2 justify-center">
                <Button 
                  onClick={triggerFileInput}
                  disabled={isUploading}
                  className="gap-2"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4" />
                      Choose File
                    </>
                  )}
                </Button>
                {(uploadedFile || error) && (
                  <Button 
                    onClick={resetState}
                    variant="outline"
                    className="gap-2"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Reset
                  </Button>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.rtf,.txt,.json,.jpg,.jpeg,.png,.bmp,.tiff"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {uploadedFile && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* PDF Viewer */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  PDF Version
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDownloadPDF}
                    className="gap-1"
                  >
                    <Download className="h-4 w-4" />
                    Download
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDeleteDocument}
                    className="gap-1 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardHeader>
                         <CardContent>
               <div className="border rounded-lg h-96 overflow-hidden">
                 <iframe
                   src={`${API_BASE_URL}/view-pdf/${uploadedFile.file_id}`}
                   className="w-full h-full"
                   title="PDF Viewer"
                   onError={() => {
                     toast.error('PDF viewer failed to load. You can still download the PDF.');
                   }}
                 />
                 <div className="text-center text-gray-500 text-sm mt-2">
                   If PDF doesn't display, use the Download button below
                 </div>
               </div>
               <div className="mt-2 text-sm text-gray-500">
                 Original file: {uploadedFile.original_filename}
               </div>
             </CardContent>
          </Card>

          {/* Text Content */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Extracted Text Content
              </CardTitle>
            </CardHeader>
                         <CardContent>
               <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
                 {uploadedFile.text_content && uploadedFile.text_content.trim() !== '' ? (
                   <pre className="whitespace-pre-wrap text-sm font-mono text-black">
                     {uploadedFile.text_content}
                   </pre>
                 ) : (
                   <div className="text-center text-gray-500 py-8">
                     <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                     <p>No text content was extracted from this document.</p>
                     <p className="text-sm">This might be an image-based document or the extraction failed.</p>
                   </div>
                 )}
               </div>
               <div className="mt-2 text-sm text-gray-500">
                 Text length: {uploadedFile.text_content?.length || 0} characters
               </div>
             </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default CVUpload;
