import React, { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Search, FileText, Eye, ExternalLink } from 'lucide-react';

interface SearchResult {
  file_id: string;
  line_number: number;
  line_text: string;
  line_type: string;
  original_filename: string;
  rank?: number;
  similarity_score?: number;
}

export const CVTextSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchType, setSearchType] = useState<'fulltext' | 'partial'>('fulltext');
  const [error, setError] = useState<string | null>(null);

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    
    try {
      const endpoint = searchType === 'fulltext' 
        ? `/api/search/cv-text?q=${encodeURIComponent(searchQuery)}`
        : `/api/search/cv-text-partial?term=${encodeURIComponent(searchQuery)}`;
      
      const response = await fetch(endpoint);
      const data = await response.json();
      
      if (data.success) {
        setSearchResults(data.results);
      } else {
        setError(data.error || 'Search failed');
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError('Search request failed');
    } finally {
      setIsSearching(false);
    }
  };

  const handleViewProfile = (fileId: string) => {
    window.open(`/cv-profile/${fileId}`, '_blank');
  };

  const getLineTypeColor = (lineType: string) => {
    switch (lineType) {
      case 'header':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'list_item':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'key_value':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'contact_info':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'date_info':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Search CV Content
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="Enter search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && performSearch()}
            className="flex-1"
          />
          <Button onClick={performSearch} disabled={isSearching}>
            {isSearching ? 'Searching...' : 'Search'}
          </Button>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant={searchType === 'fulltext' ? 'default' : 'outline'}
            onClick={() => setSearchType('fulltext')}
            size="sm"
          >
            Full-Text Search
          </Button>
          <Button
            variant={searchType === 'partial' ? 'default' : 'outline'}
            onClick={() => setSearchType('partial')}
            size="sm"
          >
            Partial Match
          </Button>
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        {searchResults.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                Found {searchResults.length} results
              </h3>
              <div className="text-sm text-muted-foreground">
                {searchType === 'fulltext' ? 'Full-text search' : 'Partial matching'}
              </div>
            </div>
            
            {searchResults.map((result, index) => (
              <Card key={index} className="p-4 hover:shadow-md transition-shadow">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getLineTypeColor(result.line_type)}`}
                        >
                          {result.line_type || 'content'}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          Line {result.line_number}
                        </span>
                        {result.rank && (
                          <Badge variant="secondary" className="text-xs">
                            Score: {result.rank.toFixed(3)}
                          </Badge>
                        )}
                        {result.similarity_score && (
                          <Badge variant="secondary" className="text-xs">
                            Similarity: {(result.similarity_score * 100).toFixed(1)}%
                          </Badge>
                        )}
                      </div>
                      
                      <h4 className="font-medium text-sm mb-1">
                        {result.original_filename}
                      </h4>
                      
                      <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded border">
                        {result.line_text}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewProfile(result.file_id)}
                      className="gap-2"
                    >
                      <Eye className="h-3 w-3" />
                      View Profile
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`/cv-profile/${result.file_id}`, '_blank')}
                      className="gap-2"
                    >
                      <ExternalLink className="h-3 w-3" />
                      Open New Tab
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {searchQuery && searchResults.length === 0 && !isSearching && !error && (
          <div className="text-center py-8 text-muted-foreground">
            <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-2">No results found</h3>
            <p className="text-sm">
              Try adjusting your search terms or using different search criteria
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
