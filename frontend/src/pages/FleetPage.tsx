import React, { useEffect, useState, useMemo, useCallback } from 'react';
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
import { Search, Filter, Download, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { ColumnVisibilityControl } from '@/components/fleet/ColumnVisibilityControl';
import { fleetService, FleetVehicle, FleetDataRequest } from '@/services/fleetService';
import { toast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface Column {
  key: string;
  label: string;
  visible: boolean;
}

const ITEMS_PER_PAGE_OPTIONS = [25, 50, 100, 200];
const COLORS = ['#f97316', '#ea580c', '#c2410c', '#9a3412', '#7c2d12'];

export const FleetPage: React.FC = () => {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState<FleetVehicle[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const [sortField, setSortField] = useState<keyof FleetVehicle>('Equipment');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedFilters, setSelectedFilters] = useState({
    make: '',
    year: '',
    location: '',
    status: '',
    department: '',
    fuel_type: '',
  });
  
  // Backend pagination data
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  
  // Summary data for charts
  const [summaryData, setSummaryData] = useState<any>(null);
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState<any>(null);

  const [columns, setColumns] = useState<Column[]>([
    { key: 'Equipment', label: 'Equipment', visible: true },
    { key: 'Make', label: 'Make', visible: true },
    { key: 'Model', label: 'Model', visible: true },
    { key: 'Year', label: 'Year', visible: true },
    { key: 'Cost', label: 'Cost', visible: true },
    { key: 'Location', label: 'Location', visible: true },
    { key: 'Status', label: 'Status', visible: true },
  ]);

  // Fetch fleet data with current filters and pagination
  const fetchFleetData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const params: FleetDataRequest = {
        page: currentPage,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        make: selectedFilters.make || undefined,
        year: selectedFilters.year ? parseInt(selectedFilters.year) : undefined,
        location: selectedFilters.location || undefined,
        status: selectedFilters.status || undefined,
        department: selectedFilters.department || undefined,
        fuel_type: selectedFilters.fuel_type || undefined,
        sort_by: sortField,
        sort_order: sortDirection,
      };
      
      console.log('Fetching fleet data with params:', params);
      
      const response = await fleetService.getFleetData(params);
      
      if (response.success) {
        setVehicles(response.data);
        setTotalCount(response.total_count);
        setTotalPages(response.total_pages);
        setHasNext(response.has_next);
        setHasPrevious(response.has_previous);
        
        toast({
          title: "Fleet Data Loaded",
          description: `Loaded ${response.data.length} vehicles (page ${response.page} of ${response.total_pages})`,
        });
        
        console.log(`Fleet data loaded: ${response.data.length} vehicles on page ${response.page}`);
      } else {
        toast({
          title: "Error Loading Fleet Data",
          description: response.message || "Failed to load fleet data",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error fetching fleet data:', error);
      toast({
        title: "Connection Error",
        description: "Unable to connect to fleet management server",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, itemsPerPage, searchTerm, selectedFilters, sortField, sortDirection]);
  
  // Fetch summary data for charts
  const fetchSummaryData = async () => {
    try {
      const response = await fleetService.getFleetSummary();
      if (response.success) {
        setSummaryData(response.summary);
      }
    } catch (error) {
      console.error('Error fetching summary data:', error);
    }
  };
  
  // Fetch filter options
  const fetchFilterOptions = async () => {
    try {
      const response = await fleetService.getFilterOptions();
      if (response.success) {
        setFilterOptions(response.options);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchSummaryData();
    fetchFilterOptions();
  }, []);
  
  // Fetch data when filters or pagination change
  useEffect(() => {
    fetchFleetData();
  }, [fetchFleetData]);

  // Chart data generation from summary data
  const chartData = useMemo(() => {
    if (!summaryData) {
      return {
        makeChart: [],
        yearChart: [],
        costChart: [],
      };
    }

    const makeChart = Object.entries(summaryData.make_distribution || {})
      .map(([name, value]) => ({ name, value: Number(value) }))
      .sort((a, b) => b.value - a.value);

    const yearChart = Object.entries(summaryData.year_distribution || {})
      .map(([name, value]) => ({ name: parseInt(name), value: Number(value) }))
      .sort((a, b) => a.name - b.name);

    const costChart = Object.entries(summaryData.cost_distribution || {})
      .map(([name, value]) => ({ name, value }));

    return {
      makeChart,
      yearChart,
      costChart,
    };
  }, [summaryData]);

  const getStatusBadge = (vehicle: FleetVehicle) => {
    const status = vehicle.Status || 'Active';
    const variants: Record<string, any> = {
      'Active': 'default',
      'Maintenance': 'warning',
      'Inactive': 'secondary',
      'Out of Service': 'destructive'
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  const handleSort = (field: keyof FleetVehicle) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  const handleFilterChange = (filterKey: string, value: string) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterKey]: value
    }));
    setCurrentPage(1); // Reset to first page when filters change
  };
  
  const handleClearFilters = () => {
    setSelectedFilters({
      make: '',
      year: '',
      location: '',
      status: '',
      department: '',
      fuel_type: '',
    });
    setCurrentPage(1);
  };
  
  const handleExport = async (format: 'excel' | 'csv' = 'excel') => {
    try {
      const params: FleetDataRequest = {
        search: searchTerm || undefined,
        make: selectedFilters.make || undefined,
        year: selectedFilters.year ? parseInt(selectedFilters.year) : undefined,
        location: selectedFilters.location || undefined,
        status: selectedFilters.status || undefined,
        department: selectedFilters.department || undefined,
        fuel_type: selectedFilters.fuel_type || undefined,
      };
      
      const response = await fleetService.exportFleetData(format, params);
      
      if (response.success) {
        toast({
          title: "Export Successful",
          description: `Exported ${response.record_count} vehicles to ${response.filename}`,
        });
      } else {
        toast({
          title: "Export Failed",
          description: response.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Export Error",
        description: "Failed to export fleet data",
        variant: "destructive",
      });
    }
  };

  const handleChartClick = (chartType: string) => {
    toast({
      title: "Chart Interaction",
      description: `Filtering table based on ${chartType} data`,
    });
    // Could implement specific filtering based on chart interaction
  };

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Fleet Management</h1>
        <div className="grid gap-6 md:grid-cols-3 mb-6">
          {[1, 2, 3].map(i => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-32 bg-muted rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-12 bg-muted rounded"></div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Fleet Management</h1>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/analytics')}>
            <BarChart className="w-4 h-4 mr-2" />
            View Analytics
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('excel')}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Vehicle
          </Button>
        </div>
      </div>

      {/* Interactive Charts */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleChartClick('make')}>
          <CardHeader>
            <CardTitle className="text-base">Fleet by Make</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData.makeChart}
                    cx="50%"
                    cy="50%"
                    outerRadius={60}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {chartData.makeChart.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleChartClick('year')}>
          <CardHeader>
            <CardTitle className="text-base">Fleet by Year</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.yearChart}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="name" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleChartClick('cost')}>
          <CardHeader>
            <CardTitle className="text-base">Cost Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.costChart}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="name" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fleet Data Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Vehicle Fleet ({totalCount.toLocaleString()} vehicles)</CardTitle>
            <div className="flex items-center space-x-2">
              <ColumnVisibilityControl 
                columns={columns} 
                onColumnChange={setColumns} 
              />
              
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search vehicles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <Select value={selectedFilters.make || 'all'} onValueChange={(value) => 
                handleFilterChange('make', value === 'all' ? '' : value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Make" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Makes</SelectItem>
                  {(filterOptions?.makes || []).map((make: string) => (
                    <SelectItem key={make} value={make}>{make}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedFilters.year || 'all'} onValueChange={(value) => 
                handleFilterChange('year', value === 'all' ? '' : value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  {(filterOptions?.years || []).map((year: number) => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedFilters.location || 'all'} onValueChange={(value) => 
                handleFilterChange('location', value === 'all' ? '' : value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  {(filterOptions?.locations || []).map((location: string) => (
                    <SelectItem key={location} value={location}>{location}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedFilters.status || 'all'} onValueChange={(value) => 
                handleFilterChange('status', value === 'all' ? '' : value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {(filterOptions?.statuses || []).map((status: string) => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {(selectedFilters.make || selectedFilters.year || selectedFilters.location || selectedFilters.status || selectedFilters.department || selectedFilters.fuel_type) && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleClearFilters}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.filter(col => col.visible).map(column => (
                    <TableHead 
                      key={column.key}
                      className="cursor-pointer hover:bg-muted"
                      onClick={() => handleSort(column.key as keyof FleetVehicle)}
                    >
                      <div className="flex items-center space-x-1">
                        <span>{column.label}</span>
                        {sortField === column.key && (
                          <span className="text-xs">
                            {sortDirection === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {vehicles.map((vehicle, index) => (
                  <TableRow key={`${vehicle.Equipment}-${index}`} className="hover:bg-muted/50">
                    {columns.filter(col => col.visible).map(column => (
                      <TableCell key={column.key}>
                        {column.key === 'Cost' ? (
                          `$${vehicle.Cost?.toLocaleString() || '0'}`
                        ) : column.key === 'Status' ? (
                          getStatusBadge(vehicle)
                        ) : column.key === 'Make' ? (
                          <span className="font-medium">{vehicle.Make} {vehicle.Model}</span>
                        ) : (
                          vehicle[column.key as keyof FleetVehicle]?.toString() || '-'
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount.toLocaleString()} vehicles
              </span>
              <Select value={itemsPerPage.toString()} onValueChange={(value) => {
                setItemsPerPage(parseInt(value));
                setCurrentPage(1);
              }}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ITEMS_PER_PAGE_OPTIONS.map(option => (
                    <SelectItem key={option} value={option.toString()}>{option}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <span className="text-sm text-muted-foreground">per page</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={!hasPrevious || isLoading}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                  if (pageNum > totalPages) return null;
                  return (
                    <Button
                      key={pageNum}
                      variant={currentPage === pageNum ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentPage(pageNum)}
                      className="w-8 h-8 p-0"
                      disabled={isLoading}
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={!hasNext || isLoading}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};