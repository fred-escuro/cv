import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Users, Eye, Upload, ArrowRight } from 'lucide-react';
import { useState, useEffect, type FC } from 'react';
import { Link } from 'react-router-dom';

interface CVSummary {
  total_count: number;
  completed_count: number;
  processing_count: number;
  error_count: number;
  recent_cvs: Array<{
    id: string;
    originalFilename: string;
    processingStatus: string;
    dateCreated: string;
    personalInfo?: {
      firstName?: string;
      lastName?: string;
    };
  }>;
}

export const CVList: FC = () => {
  const [cvSummary, setCvSummary] = useState<CVSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    const fetchCVSummary = async () => {
      try {
        // Get first page to get total count and recent CVs
        const response = await fetch(`${API_BASE_URL}/cv-list?page=1&limit=5`);
        if (response.ok) {
          const data = await response.json();
          
          // Calculate counts by status
          const statusCounts = data.cv_files.reduce((acc: any, cv: any) => {
            acc[cv.processingStatus] = (acc[cv.processingStatus] || 0) + 1;
            return acc;
          }, {});
          
          setCvSummary({
            total_count: data.pagination.total_count,
            completed_count: statusCounts.completed || 0,
            processing_count: statusCounts.processing || 0,
            error_count: statusCounts.error || 0,
            recent_cvs: data.cv_files.slice(0, 3) // Show only 3 most recent
          });
        }
      } catch (error) {
        console.error('Error fetching CV summary:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCVSummary();
  }, []);

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'border-green-600 bg-green-50 text-green-700 dark:border-green-300 dark:bg-green-100 dark:text-green-800';
      case 'processing':
        return 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800';
      case 'error':
        return 'border-red-600 bg-red-50 text-red-700 dark:border-red-300 dark:bg-red-100 dark:text-red-800';
      default:
        return 'border-muted-foreground/20 bg-muted text-muted-foreground';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">CV Management</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">...</div>
          <p className="text-xs text-muted-foreground">Loading CV data...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">CV Management</CardTitle>
        <FileText className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{cvSummary?.total_count || 0}</div>
              <p className="text-xs text-muted-foreground">Total CVs</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{cvSummary?.completed_count || 0}</div>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
          </div>

          {/* Status Breakdown */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Processing</span>
              <Badge variant="outline" className="text-xs">
                {cvSummary?.processing_count || 0}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Errors</span>
              <Badge variant="outline" className="text-xs">
                {cvSummary?.error_count || 0}
              </Badge>
            </div>
          </div>

          {/* Recent CVs */}
          {cvSummary?.recent_cvs && cvSummary.recent_cvs.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">Recent Uploads</p>
              <div className="space-y-1">
                {cvSummary.recent_cvs.map((cv) => (
                  <div key={cv.id} className="flex items-center justify-between text-xs">
                    <span className="truncate max-w-[120px]">
                      {cv.personalInfo?.firstName && cv.personalInfo?.lastName
                        ? `${cv.personalInfo.firstName} ${cv.personalInfo.lastName}`
                        : cv.originalFilename
                      }
                    </span>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getStatusBadgeColor(cv.processingStatus)}`}
                    >
                      {cv.processingStatus.charAt(0).toUpperCase() + cv.processingStatus.slice(1)}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <Link to="/cv-list" className="flex-1">
              <Button variant="outline" size="sm" className="w-full gap-2 text-xs">
                <Eye className="h-3 w-3" />
                View All
                <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
            <Link to="/cv-upload" className="flex-1">
              <Button size="sm" className="w-full gap-2 text-xs">
                <Upload className="h-3 w-3" />
                Upload
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
