import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  TrendingUp,
  Download
} from 'lucide-react';
import { ExcelDataResponse, ExcelDataRequest } from '@/services/excelDataService';

interface ExcelDataTableProps {
  data: ExcelDataResponse | null;
  loading: boolean;
  error: string | null;
  onRequestData: (params: ExcelDataRequest) => void;
  title: string;
  fileKey: string;
  onViewStats?: (column: string) => void;
}

const ITEMS_PER_PAGE_OPTIONS = [25, 50, 100, 200];

export const ExcelDataTable = ({
  data,
  loading,
  error,
  onRequestData,
  title,
  fileKey,
  onViewStats
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>({});
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [pageSize, setPageSize] = useState(50);
  const [currentPage, setCurrentPage] = useState(1);

  // Apply filters when parameters change (with debounce for search)
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      const params: ExcelDataRequest = {
        page: currentPage,
        page_size: pageSize,
        search: searchTerm || undefined,
        column_filters: Object.keys(columnFilters).length > 0 ? columnFilters : undefined,
        sort_column: sortColumn || undefined,
        sort_direction: sortDirection,
      };
      console.log('ExcelDataTable requesting data with params:', params);
      onRequestData(params);
    }, searchTerm ? 300 : 0); // 300ms debounce only for search, immediate for other changes

    return () => clearTimeout(debounceTimer);
  }, [currentPage, pageSize, searchTerm, columnFilters, sortColumn, sortDirection]); // Removed onRequestData from deps to prevent infinite loop

  // Handle column filter changes
  const handleColumnFilter = (column: string, value: string) => {
    setColumnFilters(prev => ({
      ...prev,
      [column]: value
    }));
    setCurrentPage(1); // Reset to first page
  };

  // Handle sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
    setCurrentPage(1);
  };

  // Clear all filters
  const clearFilters = () => {
    setSearchTerm('');
    setColumnFilters({});
    setSortColumn('');
    setSortDirection('asc');
    setCurrentPage(1);
  };

  // Get unique values for a column (from current data)
  const getUniqueValues = (column: string): string[] => {
    if (!data?.data) return [];
    const values = data.data.map(row => String(row[column] || '')).filter(Boolean);
    return [...new Set(values)].sort().slice(0, 20); // Limit to 20 for performance
  };

  // Handle page changes
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  // Get sort icon
  const getSortIcon = (column: string) => {
    if (sortColumn !== column) return <ArrowUpDown className="w-3 h-3" />;
    return sortDirection === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-12 bg-muted rounded animate-pulse"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-destructive">{title} - Error</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-destructive">{error}</p>
            <Button 
              onClick={() => {
                const params: ExcelDataRequest = {
                  page: currentPage,
                  page_size: pageSize,
                  search: searchTerm || undefined,
                  column_filters: Object.keys(columnFilters).length > 0 ? columnFilters : undefined,
                  sort_column: sortColumn || undefined,
                  sort_direction: sortDirection,
                };
                onRequestData(params);
              }} 
              className="mt-2"
              variant="outline"
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No data available. Click "Retry" to reload.</p>
          <Button 
            onClick={() => {
              const params: ExcelDataRequest = {
                page: currentPage,
                page_size: pageSize,
                search: searchTerm || undefined,
                column_filters: Object.keys(columnFilters).length > 0 ? columnFilters : undefined,
                sort_column: sortColumn || undefined,
                sort_direction: sortDirection,
              };
              onRequestData(params);
            }} 
            className="mt-2"
            variant="outline"
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card style={{ width: '82vw' }}>
      <CardHeader>
        <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center space-x-2">
              <span>{title}</span>
              <Badge variant="outline">
                {data.pagination?.total_rows?.toLocaleString() || '0'} records
              </Badge>
            </CardTitle>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
        
        {/* Search and Filters */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            {/* Global Search */}
            <div className="relative flex-1">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search across all columns..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="pl-8"
              />
            </div>
            
            {/* Clear Filters */}
            {(searchTerm || Object.keys(columnFilters).length > 0 || sortColumn) && (
              <Button variant="outline" size="sm" onClick={clearFilters}>
                Clear Filters
              </Button>
            )}
          </div>

          {/* Column Filters */}
          {(data.columns || []).length > 0 && (
            <div className="flex items-center space-x-2 flex-wrap gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              {(data.columns || []).slice(0, 4).map(column => (
                <Select 
                  key={column}
                  value={columnFilters[column] || 'all'}
                  onValueChange={(value) => handleColumnFilter(column, value === 'all' ? '' : value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder={column} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All {column}</SelectItem>
                    {getUniqueValues(column).map(value => (
                      <SelectItem key={value} value={value}>
                        {value}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ))}
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
                  <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto max-w-full">
              <Table className="min-w-full">
                <TableHeader>
                  <TableRow>
                    {(data.columns || []).map(column => (
                      <TableHead 
                        key={column}
                        className="cursor-pointer hover:bg-muted whitespace-nowrap min-w-[120px] px-4"
                        onClick={() => handleSort(column)}
                      >
                        <div className="flex items-center space-x-1">
                          <span className="text-sm font-medium truncate max-w-[200px]" title={column}>
                            {column}
                          </span>
                          {getSortIcon(column)}
                          {onViewStats && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-4 w-4 p-0 ml-2 flex-shrink-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                onViewStats(column);
                              }}
                            >
                              <TrendingUp className="w-3 h-3" />
                            </Button>
                          )}
                        </div>
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(data.data || []).map((row, index) => (
                    <TableRow key={index} className="hover:bg-muted/50">
                      {(data.columns || []).map(column => (
                        <TableCell key={column} className="whitespace-nowrap px-4 py-2 min-w-[120px]">
                          <div className="max-w-[200px] truncate" title={String(row[column] || '')}>
                            {typeof row[column] === 'number' && row[column] > 1000
                              ? row[column].toLocaleString()
                              : String(row[column] || '')
                            }
                          </div>
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        
        {/* Pagination */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">
              Showing {data.pagination?.start_row || 0}-{data.pagination?.end_row || 0} of{' '}
              {data.pagination?.total_rows?.toLocaleString() || '0'} records
            </span>
            <Select 
              value={pageSize.toString()} 
              onValueChange={(value) => {
                setPageSize(parseInt(value));
                setCurrentPage(1);
              }}
            >
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ITEMS_PER_PAGE_OPTIONS.map(option => (
                  <SelectItem key={option} value={option.toString()}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-sm text-muted-foreground">per page</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
              disabled={!data.pagination?.has_previous}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, data.pagination?.total_pages || 1) }, (_, i) => {
                const pageNum = Math.max(1, Math.min(
                  (data.pagination?.total_pages || 1) - 4, 
                  currentPage - 2
                )) + i;
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePageChange(pageNum)}
                    className="w-8 h-8 p-0"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(Math.min(data.pagination?.total_pages || 1, currentPage + 1))}
              disabled={!data.pagination?.has_next}
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
        
        {/* Filter Summary */}
        {data.filters_applied && (
          <div className="mt-4 p-3 bg-muted/50 rounded-lg">
            <div className="text-sm text-muted-foreground">
              <p>
                <strong>Filtered Results:</strong> {data.file_info?.total_rows_after_filter?.toLocaleString() || '0'} of{' '}
                {data.file_info?.total_rows_before_filter?.toLocaleString() || '0'} total records
              </p>
              {data.filters_applied.search_query && (
                <p><strong>Search:</strong> "{data.filters_applied.search_query}"</p>
              )}
              {data.filters_applied.sort_column && (
                <p>
                  <strong>Sort:</strong> {data.filters_applied.sort_column} ({data.filters_applied.sort_direction})
                </p>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};