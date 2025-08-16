import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { ArrowLeft, Search, Filter, FileText, Upload, Mail, Phone, MapPin, Calendar, FileType, AlertCircle, Eye, Trash2, Edit, Square, Zap, X } from 'lucide-react';
import { AdvancedSearch } from '@/components/AdvancedSearch';
import { useState, useEffect, useCallback, useRef, type FC } from 'react';
import { Link } from 'react-router-dom';

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
  convertedPdfFilename?: string; // Converted PDF filename from database
  aiOutput?: any; // AI generated JSON output
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



interface FilterOptions {
  statuses: string[];
  file_types: string[];
}

const getStatusBadgeColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'border-green-600 bg-green-50 text-green-700 dark:border-green-300 dark:bg-green-100 dark:text-green-800';
    case 'processing':
      return 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800';
    case 'error':
      return 'border-red-600 bg-red-50 text-red-700 dark:border-red-300 dark:bg-red-100 dark:text-red-800';
    case 'pending':
      return 'border-yellow-600 bg-yellow-50 text-yellow-700 dark:border-yellow-300 dark:bg-yellow-100 dark:text-yellow-800';
    default:
      return 'border-muted-foreground/20 bg-muted text-muted-foreground';
  }
};

const getFileTypeBadgeColor = (fileType: string) => {
  switch (fileType.toLowerCase()) {
    case 'pdf':
      return 'border-red-600 bg-red-50 text-red-700 dark:border-red-300 dark:bg-red-100 dark:text-red-800';
    case 'docx':
      return 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800';
    case 'doc':
      return 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800';
    default:
      return 'border-muted-foreground/20 bg-muted text-muted-foreground';
  }
};

// Loading skeleton component for CV cards
const CVCardSkeleton: FC = () => (
  <Card className="h-[380px] animate-pulse">
    <CardContent className="pr-6 pl-6 h-full flex flex-col">
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-muted rounded w-3/4"></div>
        <div className="h-3 bg-muted rounded w-1/2"></div>
        <div className="flex gap-2">
          <div className="h-5 bg-muted rounded w-16"></div>
          <div className="h-5 bg-muted rounded w-20"></div>
        </div>
        <div className="h-3 bg-muted rounded w-24"></div>
        <div className="space-y-2">
          <div className="h-3 bg-muted rounded w-full"></div>
          <div className="h-3 bg-muted rounded w-3/4"></div>
          <div className="h-3 bg-muted rounded w-1/2"></div>
        </div>
        <div className="space-y-2">
          <div className="h-3 bg-muted rounded w-16"></div>
          <div className="flex gap-2">
            <div className="h-5 bg-muted rounded flex-1"></div>
            <div className="h-5 bg-muted rounded flex-1"></div>
          </div>
          <div className="flex gap-2">
            <div className="h-5 bg-muted rounded flex-1"></div>
            <div className="h-5 bg-muted rounded flex-1"></div>
          </div>
          <div className="flex gap-2">
            <div className="h-5 bg-muted rounded flex-1"></div>
            <div className="h-5 bg-muted rounded flex-1"></div>
          </div>
        </div>
      </div>
      <div className="flex gap-1 pt-4 mt-auto border-t border-border">
        <div className="h-7 bg-muted rounded flex-1"></div>
        <div className="h-7 bg-muted rounded flex-1"></div>
        <div className="h-7 bg-muted rounded flex-1"></div>
        <div className="h-7 bg-muted rounded w-10"></div>
      </div>
    </CardContent>
  </Card>
);

export const CVListPage: FC = () => {
  const [cvFiles, setCvFiles] = useState<CVFile[]>([]);
  const [allCvFiles, setAllCvFiles] = useState<CVFile[]>([]); // Store all CVs for local filtering

  const [filterOptions, setFilterOptions] = useState<FilterOptions>({ statuses: [], file_types: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<string>('both');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all');
  const [isAdvancedSearch, setIsAdvancedSearch] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false); // Separate loading state for search
  const [error, setError] = useState<string | null>(null);
  const API_BASE_URL = 'http://localhost:8000';
  
  // Ref to access advanced search clear function
  const advancedSearchRef = useRef<{ clearQuery: () => void }>(null);

  // Clear search function
  const clearSearch = () => {
    setSearchQuery('');
    setCurrentPage(1);
    // Reset to show all CVs
    fetchCVList(1, '', searchType, statusFilter, fileTypeFilter);
  };

  // Fetch CV list data
  const fetchCVList = async (page: number = 1, search: string = '', searchType: string = 'both', status: string = 'all', fileType: string = 'all') => {
    try {
      setIsLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '1000' // Fetch more data for local filtering
      });
      
      if (search) params.append('search', search);
      if (searchType !== 'both') params.append('search_type', searchType);
      if (status !== 'all') params.append('status_filter', status);
      if (fileType !== 'all') params.append('file_type_filter', fileType);
      
      const response = await fetch(`${API_BASE_URL}/cv-list?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🔍 Backend search response:', data); // Debug log
      setAllCvFiles(data.cv_files); // Store all CVs
      setCvFiles(data.cv_files); // Set initial display
      
    } catch (err) {
      console.error('Error fetching CV list:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch CV list');
    } finally {
      setIsLoading(false);
    }
  };

  // Local filtering function
  const filterCvFiles = useCallback((cvFiles: CVFile[], search: string, status: string, fileType: string) => {
    return cvFiles.filter(cv => {
      // Status filter
      if (status !== 'all' && cv.processingStatus !== status) {
        return false;
      }
      
      // File type filter
      if (fileType !== 'all' && cv.fileType.toLowerCase() !== fileType.toLowerCase()) {
        return false;
      }
      
      // Search filter
      if (search) {
        const searchLower = search.toLowerCase();
        const searchableText = [
          cv.originalFilename,
          cv.personalInfo?.firstName || '',
          cv.personalInfo?.lastName || '',
          cv.personalInfo?.emails?.map(e => e.email).join(' ') || '',
          cv.personalInfo?.phones?.map(p => p.phone).join(' ') || '',
          cv.personalInfo?.city || '',
          cv.personalInfo?.state || '',
          cv.personalInfo?.country || '',
          cv.workExperience?.map(w => `${w.jobTitle} ${w.companyName}`).join(' ') || '',
          cv.education?.map(e => `${e.degree} ${e.institution}`).join(' ') || '',
          cv.skills?.map(s => s.skillName).join(' ') || ''
        ].join(' ').toLowerCase();
        
        return searchableText.includes(searchLower);
      }
      
      return true;
    });
  }, []);



  // Apply filters when status or file type filters change (no automatic search)
  useEffect(() => {
    if (allCvFiles.length > 0 && !searchQuery) {
      setIsSearching(true);
      const timer = setTimeout(() => {
        const filtered = filterCvFiles(allCvFiles, '', statusFilter, fileTypeFilter);
        setCvFiles(filtered);
        setCurrentPage(1); // Reset to first page
        setIsSearching(false);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [allCvFiles.length, statusFilter, fileTypeFilter, filterCvFiles]);

  // Fetch filter options
  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cv-list/filters`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setFilterOptions(data);
      
    } catch (err) {
      console.error('Error fetching filter options:', err);
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchFilterOptions();
    fetchCVList(1, '', searchType, 'all', 'all');
  }, []);

  // Handle search input change (no API call, just update local state)
  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  // Handle search submission
  const handleSearch = () => {
    if (searchQuery.trim()) {
      setCurrentPage(1); // Reset to first page
      fetchCVList(1, searchQuery, searchType, statusFilter, fileTypeFilter);
    }
  };

  // Handle advanced search
  const handleAdvancedSearch = async (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page
    setIsSearching(true);
    
    try {
      // Call the advanced search API endpoint
      const response = await fetch(`${API_BASE_URL}/api/search/cv-advanced?q=${encodeURIComponent(query)}&limit=1000`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🔍 Advanced search response:', data);
      
              if (data.success && data.results) {
          // First, get all CV files to have the complete data
          const allCvResponse = await fetch(`${API_BASE_URL}/cv-list?page=1&limit=1000`);
          if (allCvResponse.ok) {
            const allCvData = await allCvResponse.json();
            const allCvFiles = allCvData.cv_files;
            
            // Filter to only include CVs that were found in the advanced search
            const searchResultFileIds = new Set(data.results.map((r: any) => r.file_id));
            const filteredCvFiles = allCvFiles.filter((cv: CVFile) => searchResultFileIds.has(cv.fileId));
            
            setAllCvFiles(filteredCvFiles);
            setCvFiles(filteredCvFiles);
          }
        } else {
        // Fallback to simple search if advanced search fails
        fetchCVList(1, query, searchType, statusFilter, fileTypeFilter);
      }
    } catch (err) {
      console.error('Advanced search failed, falling back to simple search:', err);
      // Fallback to simple search
      fetchCVList(1, query, searchType, statusFilter, fileTypeFilter);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle status filter change
  const handleStatusFilterChange = (status: string) => {
    setStatusFilter(status);
  };

  // Handle file type filter change
  const handleFileTypeFilterChange = (fileType: string) => {
    setFileTypeFilter(fileType);
  };

  // Handle search type change
  const handleSearchTypeChange = (newSearchType: string) => {
    setSearchType(newSearchType);
    // Trigger a new search with the updated search type
    if (searchQuery) {
      fetchCVList(1, searchQuery, newSearchType, statusFilter, fileTypeFilter);
    }
  };

  // Pagination for filtered results
  const itemsPerPage = 20;
  const totalPages = Math.ceil(cvFiles.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentPageCvFiles = cvFiles.slice(startIndex, endIndex);

  // Handle pagination
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Get primary contact info
  const getPrimaryContact = (cv: CVFile) => {
    const primaryEmail = cv.personalInfo?.emails?.[0]?.email;
    const primaryPhone = cv.personalInfo?.phones?.[0]?.phone;
    return { email: primaryEmail, phone: primaryPhone };
  };

  // Get primary location
  const getPrimaryLocation = (cv: CVFile) => {
    const city = cv.personalInfo?.city;
    const state = cv.personalInfo?.state;
    const country = cv.personalInfo?.country;
    
    if (city && state) return `${city}, ${state}`;
    if (city) return city;
    if (state) return state;
    if (country) return country;
    return 'Location not specified';
  };

  // Calculate total years of experience
  const calculateYearsOfExperience = (workExperience: CVFile['workExperience']): number => {
    if (!workExperience || workExperience.length === 0) {
      return 0;
    }

    const now = new Date();
    let totalYears = 0;

    for (const job of workExperience) {
      let startDate: Date;
      let endDate: Date;

      if (job.startDate) {
        startDate = new Date(job.startDate);
      } else {
        startDate = new Date(0); // Unix epoch
      }

      if (job.endDate) {
        endDate = new Date(job.endDate);
      } else {
        endDate = now;
      }

      const diffTime = Math.abs(endDate.getTime() - startDate.getTime());
      const diffYears = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 365.25));
      totalYears += diffYears;
    }

    return totalYears;
  };

  // Get unique job positions with total duration from work experience
  const getUniqueJobPositionsWithDuration = (workExperience: CVFile['workExperience']): Array<{position: string, totalDuration: number}> => {
    if (!workExperience || workExperience.length === 0) {
      return [];
    }
    
    // Group by job title and sum up durations
    const positionMap = new Map<string, number>();
    
    workExperience.forEach(job => {
      if (job.jobTitle && job.jobTitle.trim() !== '') {
        const duration = calculateJobDuration(job.startDate, job.endDate);
        const existingDuration = positionMap.get(job.jobTitle) || 0;
        positionMap.set(job.jobTitle, existingDuration + duration);
      }
    });
    
    // Convert to array and sort by duration (descending)
    return Array.from(positionMap.entries())
      .map(([position, totalDuration]) => ({ position, totalDuration }))
      .sort((a, b) => b.totalDuration - a.totalDuration);
  };

  // Calculate duration between start and end dates in months
  const calculateJobDuration = (startDate: string | null | undefined, endDate: string | null | undefined): number => {
    if (!startDate) return 0;
    
    const start = new Date(startDate);
    const end = endDate ? new Date(endDate) : new Date(); // Use current date if no end date
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0;
    
    const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    return Math.max(0, months);
  };

  // Format duration for display (years and months)
  const formatDuration = (months: number): string => {
    if (months === 0) return '0m';
    if (months < 12) return `${months}m`;
    
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    
    if (remainingMonths === 0) return `${years}y`;
    return `${years}y ${remainingMonths}m`;
  };

  const handleViewProfile = (cv: CVFile) => {
    // Open the profile page in a new tab
    window.open(`/cv-profile/${cv.fileId}`, '_blank');
  };

  

  const handleStopProcessing = async (cv: CVFile) => {
    if (window.confirm(`Are you sure you want to stop processing CV "${cv.originalFilename}"?`)) {
      try {
        const response = await fetch(`${API_BASE_URL}/cv/${cv.fileId}/stop`, {
          method: 'POST',
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to stop processing');
        }

        const result = await response.json();
        alert(`Processing stopped successfully: ${result.message}`);
        
        // Refresh the CV list to show updated status
        fetchCVList(currentPage, searchQuery, searchType, statusFilter, fileTypeFilter);
        
      } catch (err) {
        console.error('Error stopping CV processing:', err);
        const errorMessage = err instanceof Error ? err.message : 'Failed to stop CV processing';
        alert(`Failed to stop CV processing: ${errorMessage}`);
      }
    }
  };

  const handleDeleteCV = async (cv: CVFile) => {
    if (window.confirm(`Are you sure you want to delete CV "${cv.originalFilename}"? This action cannot be undone.`)) {
      try {
        const response = await fetch(`${API_BASE_URL}/delete-cv/${cv.id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        setCvFiles(cvFiles.filter(file => file.id !== cv.id));
        alert('CV deleted successfully!');
        fetchCVList(currentPage, searchQuery, searchType, statusFilter, fileTypeFilter); // Re-fetch to update pagination
      } catch (err) {
        console.error('Error deleting CV:', err);
        alert('Failed to delete CV.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
             <PageWrapper className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-2">
        {/* Header Section */}
        <PageSection index={0}>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-4">
                <Link to="/">
                  <Button variant="ghost" size="sm" className="gap-2">
                    <ArrowLeft className="h-4 w-4" />
                    Back to Dashboard
                  </Button>
                </Link>
              </div>
              
              <Link to="/cv-upload">
                <Button className="gap-2">
                  <Upload className="h-4 w-4" />
                  Upload CV
                </Button>
              </Link>
            </div>
            
            <div className="space-y-1">
              <h1 className="text-2xl font-bold tracking-tight">CV List</h1>
              <p className="text-muted-foreground">
                Browse and search through all uploaded CVs in the system
              </p>
            </div>
          </div>
        </PageSection>

        {/* Search & Filters Section */}
        <PageSection index={1}>
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Search & Filter</CardTitle>
                <Button
                  variant={isAdvancedSearch ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    // Clear search fields when switching modes
                    setSearchQuery('');
                    if (advancedSearchRef.current) {
                      advancedSearchRef.current.clearQuery();
                    }
                    // Reset to first page and refresh CV list to show all CVs when switching modes
                    setCurrentPage(1);
                    fetchCVList(1, '', searchType, statusFilter, fileTypeFilter);
                    setIsAdvancedSearch(!isAdvancedSearch);
                  }}
                  className="gap-2"
                >
                  <Zap className="h-4 w-4" />
                  {isAdvancedSearch ? "Simple Search" : "Advanced Search"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isAdvancedSearch ? (
                <AdvancedSearch 
                  ref={advancedSearchRef}
                  onSearch={handleAdvancedSearch} 
                  isSearching={isSearching}
                />
              ) : (
                <>
                  <div className="space-y-4">
                    {/* Search Row */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      {/* Search Input */}
                      <div className="flex-1">
                        <div className="relative">
                          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input
                            placeholder="Search by name, email, content, or filename..."
                            value={searchQuery}
                            onChange={(e) => handleSearchChange(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                            className="pl-10"
                          />
                          {isSearching && (
                            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                              <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Search Actions */}
                      <div className="flex gap-2">
                        <Button 
                          onClick={handleSearch}
                          disabled={isSearching || !searchQuery.trim()}
                          className="gap-2 min-w-[100px]"
                        >
                          <Search className="h-4 w-4" />
                          Search
                        </Button>
                        
                        <Button 
                          variant="outline"
                          onClick={clearSearch}
                          disabled={isSearching || !searchQuery.trim()}
                          className="gap-2 min-w-[100px]"
                        >
                          <X className="h-4 w-4" />
                          Clear
                        </Button>
                      </div>
                    </div>
                    
                    {/* Filters Row */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      {/* Search Type Selector */}
                      <div className="sm:w-48">
                        <Select value={searchType} onValueChange={handleSearchTypeChange}>
                          <SelectTrigger className="gap-2">
                            <Search className="h-4 w-4" />
                            <SelectValue placeholder="Search type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="both">Full-text + Fields</SelectItem>
                            <SelectItem value="fulltext">Full-text Only</SelectItem>
                            <SelectItem value="fielded">Fields Only</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      {/* Status Filter */}
                      <div className="sm:w-48">
                        <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
                          <SelectTrigger className="gap-2">
                            <Filter className="h-4 w-4" />
                            <SelectValue placeholder="Filter by status" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Statuses</SelectItem>
                            {filterOptions.statuses.map((status) => (
                              <SelectItem key={status} value={status}>
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      {/* File Type Filter */}
                      <div className="sm:w-48">
                        <Select value={fileTypeFilter} onValueChange={handleFileTypeFilterChange}>
                          <SelectTrigger className="gap-2">
                            <FileType className="h-4 w-4" />
                            <SelectValue placeholder="Filter by file type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All File Types</SelectItem>
                            {filterOptions.file_types.map((fileType) => (
                              <SelectItem key={fileType} value={fileType.toUpperCase()}>
                                {fileType.toUpperCase()}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                  
                  {/* Results Count */}
                  <div className="mt-4 text-sm text-muted-foreground">
                    {isSearching ? (
                      <span>Searching...</span>
                    ) : (
                      <div className="space-y-1">
                        <div>
                          {searchQuery ? (
                            <span>
                              Found {cvFiles.length} CV{cvFiles.length !== 1 ? 's' : ''} for "{searchQuery}"
                            </span>
                          ) : (
                            <span>
                              Showing {currentPageCvFiles.length} of {cvFiles.length} CVs
                              {cvFiles.length !== allCvFiles.length && ` (filtered from ${allCvFiles.length} total)`}
                            </span>
                          )}
                        </div>
                        {searchQuery && (
                          <div className="text-xs">
                            Search type: {searchType === 'both' ? 'Full-text + Fields' : 
                                         searchType === 'fulltext' ? 'Full-text Only' : 'Fields Only'}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </PageSection>

        {/* CV List */}
        <PageSection index={2} className="mt-4">
          {isLoading ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="h-12 w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <FileText className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium">Loading CVs...</h3>
                  <p className="text-sm text-muted-foreground">
                    Please wait while we fetch the CV list
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : error ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="h-12 w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <AlertCircle className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium">Error loading CVs</h3>
                  <p className="text-sm text-muted-foreground">
                    {error}
                  </p>
                  <Button 
                    variant="outline" 
                    onClick={() => fetchCVList(1, '', searchType, 'all', 'all')}
                    className="mt-4"
                  >
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : cvFiles.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="h-12 w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <Search className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium">No CVs found</h3>
                  <p className="text-sm text-muted-foreground">
                    {searchQuery || statusFilter !== 'all' || fileTypeFilter !== 'all' 
                      ? 'Try adjusting your search or filter criteria'
                      : 'No CVs have been uploaded yet'
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
                            {/* CV Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {isSearching ? (
                  // Show loading skeletons while searching
                  Array.from({ length: 6 }).map((_, index) => (
                    <PageSection key={`skeleton-${index}`} index={index + 3}>
                      <CVCardSkeleton />
                    </PageSection>
                  ))
                ) : (
                  currentPageCvFiles.map((cv, index) => (
                    <PageSection key={cv.id} index={index + 3}>
                      <Card className="hover:shadow-md transition-shadow h-[380px]">
                        <CardContent className="pr-6 pl-6 h-full flex flex-col">
                          {/* Content Section */}
                          <div className="flex-1 space-y-2 overflow-hidden">
                            {/* Name and Latest Job Position */}
                            <div>
                              <h3 className="font-medium truncate text-sm">
                                {cv.personalInfo?.firstName && cv.personalInfo?.lastName 
                                  ? `${cv.personalInfo.firstName} ${cv.personalInfo.lastName}`
                                  : cv.originalFilename
                                }
                              </h3>
                              {cv.workExperience && cv.workExperience.length > 0 && (
                                <p className="font-bold text-xs text-muted-foreground truncate">
                                  {cv.workExperience[0].jobTitle} at {cv.workExperience[0].companyName}
                                </p>
                              )}
                            </div>
                            
                            {/* Badges */}
                            <div className="flex flex-wrap gap-1">
                              <Badge 
                                variant="outline"
                                className={`text-xs ${getStatusBadgeColor(cv.processingStatus)}`}
                              >
                                {cv.processingStatus.charAt(0).toUpperCase() + cv.processingStatus.slice(1)}
                              </Badge>
                              <Badge 
                                variant="outline"
                                className={`text-xs ${getFileTypeBadgeColor(cv.fileType)}`}
                              >
                                {cv.fileType.toUpperCase()}
                              </Badge>
                              {cv.workExperience && cv.workExperience.length > 0 && (
                                <Badge 
                                  variant="outline"
                                  className="text-xs border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800"
                                >
                                  {calculateYearsOfExperience(cv.workExperience)} years exp
                                </Badge>
                              )}
                            </div>

                            {/* Upload Date */}
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Calendar className="h-3 w-3" />
                              <span>Uploaded {formatDate(cv.dateCreated)}</span>
                            </div>

                            {/* Contact Information */}
                            {cv.personalInfo && (
                              <div className="space-y-1">
                                {getPrimaryContact(cv).email && (
                                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <Mail className="h-3 w-3" />
                                    <span className="truncate">{getPrimaryContact(cv).email}</span>
                                  </div>
                                )}
                                {getPrimaryContact(cv).phone && (
                                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <Phone className="h-3 w-3" />
                                    <span>{getPrimaryContact(cv).phone}</span>
                                  </div>
                                )}
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                  <MapPin className="h-3 w-3" />
                                  <span className="truncate">{getPrimaryLocation(cv)}</span>
                                </div>
                                
                                {/* Job Positions Section - Show unique job positions, fallback to skills if no work experience */}
                                <div className="pt-2 pb-2">
                                  <div className="text-xs text-muted-foreground mb-2 font-medium">
                                    {cv.workExperience && cv.workExperience.length > 0 ? 'Job Positions:' : 'Skills:'}
                                  </div>
                                  <div className="space-y-2 min-h-[60px]">
                                    {(() => {
                                      if (cv.workExperience && cv.workExperience.length > 0) {
                                        // Show job positions in a scrollable container
                                        const uniquePositions = getUniqueJobPositionsWithDuration(cv.workExperience);
                                        if (uniquePositions.length === 0) {
                                          return (
                                            <span className="text-xs text-muted-foreground/50 italic flex-1 text-center">No job titles listed</span>
                                          );
                                        }
                                        
                                        return (
                                          <div className="max-h-24 overflow-y-auto">
                                            <div className="flex flex-wrap gap-2 p-1">
                                              {uniquePositions.map(({ position, totalDuration }, index) => (
                                                <div key={index} className="flex items-center gap-1">
                                                  <span className="text-xs border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800 border px-2 py-1 rounded-md">
                                                    {position}
                                                  </span>
                                                  <span className="text-xs bg-red-700 dark:bg-red-600 text-white px-1.5 py-0.5 rounded text-[10px] font-medium">
                                                    {formatDuration(totalDuration)}
                                                  </span>
                                                </div>
                                              ))}
                                            </div>
                                          </div>
                                        );
                                      } else {
                                        // Fallback to skills if no work experience
                                        if (!cv.skills || cv.skills.length === 0) {
                                          return (
                                            <span className="text-xs text-muted-foreground/50 italic flex-1 text-center">No skills listed</span>
                                          );
                                        }
                                        
                                        return (
                                          <div className="max-h-24 overflow-y-auto">
                                            <div className="flex flex-wrap gap-2 p-1">
                                              {cv.skills.map((skill, skillIndex) => (
                                                <span 
                                                  key={skillIndex}
                                                  className="text-xs bg-muted px-2 py-1 rounded-md text-muted-foreground"
                                                >
                                                  {skill.skillName}
                                                </span>
                                              ))}
                                            </div>
                                          </div>
                                        );
                                      }
                                    })()}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Action Buttons - Fixed at bottom with proper spacing */}
                          <div className="flex gap-1 pt-4 mt-auto border-t border-border">
                            {/* Stop Button for Processing Files */}
                            {cv.processingStatus === 'processing' && (
                              <Button
                                variant="destructive"
                                size="sm"
                                className="gap-1 text-xs h-7 px-2"
                                onClick={() => handleStopProcessing(cv)}
                              >
                                <Square className="h-3 w-3" />
                                Stop
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1 gap-1 text-xs h-7"
                              onClick={() => handleViewProfile(cv)}
                            >
                              <Eye className="h-3 w-3" />
                              View Profile
                            </Button>
                            <Link to={`/edit-candidate/${cv.fileId}`}>
                              <Button
                                variant="outline"
                                size="sm"
                                className="flex-1 gap-1 text-xs h-7"
                              >
                                <Edit className="h-3 w-3" />
                                Edit
                              </Button>
                            </Link>
                            <Button
                              variant="outline"
                              size="sm"
                              className="gap-1 text-xs h-7 px-2"
                              onClick={() => handleDeleteCV(cv)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </PageSection>
                  ))
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex items-center justify-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      
                      return (
                        <Button
                          key={pageNum}
                          variant={currentPage === pageNum ? "default" : "outline"}
                          size="sm"
                          onClick={() => handlePageChange(pageNum)}
                          className="w-10"
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
                 </PageSection>
       </PageWrapper>



       
     </div>
   );
 };
