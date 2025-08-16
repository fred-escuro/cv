import React, { useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, X, HelpCircle, BookOpen } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface AdvancedSearchProps {
  onSearch: (query: string) => void;
  isSearching?: boolean;
}

interface SearchExample {
  title: string;
  query: string;
  description: string;
}

const SEARCH_EXAMPLES: SearchExample[] = [
  {
    title: "Exact Match",
    query: "CLARITY AND PLDT",
    description: "Find CVs containing both 'CLARITY' and 'PLDT'"
  },
  {
    title: "Either/Or",
    query: "Systems OR Analyst",
    description: "Find CVs containing either 'Systems' or 'Analyst'"
  },
  {
    title: "Complex Logic",
    query: "(Business OR IT) AND (Analyst OR Developer)",
    description: "Find CVs with Business/IT AND Analyst/Developer"
  },
  {
    title: "Location + Skills",
    query: "Philippines AND (Java OR Python)",
    description: "Find CVs from Philippines with Java or Python skills"
  },
  {
    title: "Company + Role",
    query: "PLDT AND (Manager OR Director)",
    description: "Find CVs mentioning PLDT with Manager or Director roles"
  }
];

export const AdvancedSearch = forwardRef<{ clearQuery: () => void }, AdvancedSearchProps>(({ onSearch, isSearching = false }, ref) => {
  const [query, setQuery] = useState('');
  const [showExamples, setShowExamples] = useState(false);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  // Expose clearQuery function to parent component
  useImperativeHandle(ref, () => ({
    clearQuery: () => setQuery('')
  }));

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query.trim());
      
      // Add to history
      setQueryHistory(prev => {
        const newHistory = [query.trim(), ...prev.filter(q => q !== query.trim())];
        return newHistory.slice(0, 5); // Keep last 5 queries
      });
    }
  }, [query, onSearch]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const useExample = (exampleQuery: string) => {
    setQuery(exampleQuery);
    setShowExamples(false);
  };

  const clearQuery = () => {
    setQuery('');
  };

  const addOperator = (operator: string) => {
    if (query.trim()) {
      setQuery(prev => `${prev.trim()} ${operator} `);
    } else {
      setQuery(`${operator} `);
    }
  };

  const addParentheses = () => {
    setQuery(prev => `${prev.trim()} ( )`);
  };

  const removeFromHistory = (index: number) => {
    setQueryHistory(prev => prev.filter((_, i) => i !== index));
  };

  const useHistoryQuery = (historyQuery: string) => {
    setQuery(historyQuery);
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5" />
            Advanced Search
          </CardTitle>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowExamples(!showExamples)}
                    className="h-8 w-8 p-0"
                  >
                    <HelpCircle className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Show search examples</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Use AND, OR operators and parentheses for complex searches
        </p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Search Input */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              placeholder="Enter advanced search query (e.g., CLARITY AND PLDT)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button
              onClick={handleSearch}
              disabled={isSearching || !query.trim()}
              className="gap-2"
            >
              <Search className="h-4 w-4" />
              Search
            </Button>
            {query && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearQuery}
                className="h-10 w-10 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          {/* Quick Operators */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => addOperator('AND')}
              className="text-xs h-7"
            >
              + AND
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addOperator('OR')}
              className="text-xs h-7"
            >
              + OR
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={addParentheses}
              className="text-xs h-7"
            >
              + ( )
            </Button>
          </div>
        </div>

        {/* Search History */}
        {queryHistory.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Recent Searches</h4>
            <div className="flex flex-wrap gap-2">
              {queryHistory.map((historyQuery, index) => (
                <div key={index} className="flex items-center gap-1">
                  <Badge
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                    onClick={() => useHistoryQuery(historyQuery)}
                  >
                    {historyQuery}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFromHistory(index)}
                    className="h-5 w-5 p-0 hover:bg-destructive hover:text-destructive-foreground"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search Examples */}
        {showExamples && (
          <div className="space-y-3 pt-2 border-t">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Search Examples
            </h4>
            <div className="grid gap-3">
              {SEARCH_EXAMPLES.map((example, index) => (
                <div key={index} className="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-medium text-sm">{example.title}</h5>
                      <p className="text-sm text-muted-foreground mt-1">
                        {example.description}
                      </p>
                      <code className="text-xs bg-muted px-2 py-1 rounded mt-2 inline-block">
                        {example.query}
                      </code>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => useExample(example.query)}
                      className="ml-2"
                    >
                      Use
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search Tips */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p><strong>Tips:</strong></p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Use <code className="bg-muted px-1 rounded">AND</code> to find CVs with both terms</li>
            <li>Use <code className="bg-muted px-1 rounded">OR</code> to find CVs with either term</li>
            <li>Use <code className="bg-muted px-1 rounded">( )</code> to group complex expressions</li>
            <li>Operators are case-insensitive</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
});
