import React, { useEffect, useState, useMemo } from 'react';
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
import { apiService, VehicleData } from '@/services/apiService';
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
  const [vehicles, setVehicles] = useState<VehicleData[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<VehicleData[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const [sortField, setSortField] = useState<keyof VehicleData>('Equipment');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedFilters, setSelectedFilters] = useState({
    make: '',
    year: '',
    location: '',
  });

  const [columns, setColumns] = useState<Column[]>([
    { key: 'Equipment', label: 'Equipment', visible: true },
    { key: 'Make', label: 'Make', visible: true },
    { key: 'Model', label: 'Model', visible: true },
    { key: 'Year', label: 'Year', visible: true },
    { key: 'Cost', label: 'Cost', visible: true },
    { key: 'Location', label: 'Location', visible: true },
    { key: 'Status', label: 'Status', visible: true },
  ]);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await apiService.getVehicleFleetData();
        if (response.success && response.data) {
          // API returns { data: VehicleData[], columns: string[], row_count: number }
          const vehicleData = response.data.data || [];
          setVehicles(vehicleData);
          setFilteredVehicles(vehicleData);
          
          if (vehicleData.length > 0) {
            toast({
              title: "Data Loaded",
              description: `Loaded ${response.data.row_count || vehicleData.length} vehicles from server`,
            });
          }
        } else {
          // Generate demo data for testing
          const demoData = Array.from({ length: 500 }, (_, i) => ({
            Equipment: `FL-${String(i + 1).padStart(4, '0')}`,
            Make: ['Ford', 'Chevrolet', 'Toyota', 'Honda', 'Nissan'][i % 5],
            Model: ['F-150', 'Silverado', 'Camry', 'Accord', 'Altima'][i % 5],
            Year: 2018 + (i % 6),
            Cost: Math.floor(Math.random() * 50000) + 20000,
            Location: ['Newark', 'Trenton', 'Camden', 'Paterson', 'Edison'][i % 5],
            Status: ['Active', 'Maintenance', 'Inactive'][i % 3],
          }));
          setVehicles(demoData);
          setFilteredVehicles(demoData);
          
          toast({
            title: "Demo Mode",
            description: "Using demo data - upload fleet data to see real information",
            variant: "default",
          });
        }
      } catch (error) {
        // Generate demo data on error
        const demoData = Array.from({ length: 500 }, (_, i) => ({
          Equipment: `FL-${String(i + 1).padStart(4, '0')}`,
          Make: ['Ford', 'Chevrolet', 'Toyota', 'Honda', 'Nissan'][i % 5],
          Model: ['F-150', 'Silverado', 'Camry', 'Accord', 'Altima'][i % 5],
          Year: 2018 + (i % 6),
          Cost: Math.floor(Math.random() * 50000) + 20000,
          Location: ['Newark', 'Trenton', 'Camden', 'Paterson', 'Edison'][i % 5],
          Status: ['Active', 'Maintenance', 'Inactive'][i % 3],
        }));
        setVehicles(demoData);
        setFilteredVehicles(demoData);
        
        toast({
          title: "Connection Error",
          description: "Unable to connect to server, showing demo data",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchVehicles();
  }, []);

  // Filter and search logic
  useEffect(() => {
    let filtered = vehicles.filter(vehicle => {
      const matchesSearch = Object.values(vehicle).some(value =>
        value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      const matchesMake = !selectedFilters.make || vehicle.Make === selectedFilters.make;
      const matchesYear = !selectedFilters.year || vehicle.Year.toString() === selectedFilters.year;
      const matchesLocation = !selectedFilters.location || vehicle.Location === selectedFilters.location;
      
      return matchesSearch && matchesMake && matchesYear && matchesLocation;
    });

    // Sort filtered results
    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredVehicles(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchTerm, selectedFilters, vehicles, sortField, sortDirection]);

  // Pagination logic
  const totalPages = Math.ceil(filteredVehicles.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentVehicles = filteredVehicles.slice(startIndex, endIndex);

  // Chart data generation
  const chartData = useMemo(() => {
    const makeData = filteredVehicles.reduce((acc, vehicle) => {
      acc[vehicle.Make] = (acc[vehicle.Make] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const yearData = filteredVehicles.reduce((acc, vehicle) => {
      acc[vehicle.Year] = (acc[vehicle.Year] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const costData = filteredVehicles.reduce((acc, vehicle) => {
      const range = vehicle.Cost < 30000 ? '<$30k' : 
                   vehicle.Cost < 50000 ? '$30k-$50k' : '>$50k';
      acc[range] = (acc[range] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      makeChart: Object.entries(makeData).map(([name, value]) => ({ name, value })),
      yearChart: Object.entries(yearData).map(([name, value]) => ({ name: parseInt(name), value })).sort((a, b) => a.name - b.name),
      costChart: Object.entries(costData).map(([name, value]) => ({ name, value })),
    };
  }, [filteredVehicles]);

  const getStatusBadge = (vehicle: VehicleData) => {
    const status = vehicle.Status || 'Active';
    const variants: Record<string, any> = {
      'Active': 'default',
      'Maintenance': 'warning',
      'Inactive': 'secondary'
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  const handleSort = (field: keyof VehicleData) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleChartClick = (chartType: string) => {
    toast({
      title: "Chart Interaction",
      description: `Filtering table based on ${chartType} data`,
    });
    // Could implement specific filtering based on chart interaction
  };

  const uniqueValues = {
    makes: [...new Set(vehicles.map(v => v.Make))].sort(),
    years: [...new Set(vehicles.map(v => v.Year))].sort((a, b) => b - a),
    locations: [...new Set(vehicles.map(v => v.Location))].sort(),
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
          <Button variant="outline" size="sm">
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
            <CardTitle>Vehicle Fleet ({filteredVehicles.length.toLocaleString()} vehicles)</CardTitle>
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
              <Select value={selectedFilters.make} onValueChange={(value) => 
                setSelectedFilters(prev => ({ ...prev, make: value }))}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Make" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Makes</SelectItem>
                  {uniqueValues.makes.map(make => (
                    <SelectItem key={make} value={make}>{make}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedFilters.year} onValueChange={(value) => 
                setSelectedFilters(prev => ({ ...prev, year: value }))}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Years</SelectItem>
                  {uniqueValues.years.map(year => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedFilters.location} onValueChange={(value) => 
                setSelectedFilters(prev => ({ ...prev, location: value }))}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Locations</SelectItem>
                  {uniqueValues.locations.map(location => (
                    <SelectItem key={location} value={location}>{location}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {(selectedFilters.make || selectedFilters.year || selectedFilters.location) && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setSelectedFilters({ make: '', year: '', location: '' })}
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
                      onClick={() => handleSort(column.key as keyof VehicleData)}
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
                {currentVehicles.map((vehicle, index) => (
                  <TableRow key={index} className="hover:bg-muted/50">
                    {columns.filter(col => col.visible).map(column => (
                      <TableCell key={column.key}>
                        {column.key === 'Cost' ? (
                          `$${vehicle.Cost?.toLocaleString() || '0'}`
                        ) : column.key === 'Status' ? (
                          getStatusBadge(vehicle)
                        ) : column.key === 'Make' ? (
                          <span className="font-medium">{vehicle.Make} {vehicle.Model}</span>
                        ) : (
                          vehicle[column.key as keyof VehicleData]?.toString() || '-'
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
                Showing {startIndex + 1}-{Math.min(endIndex, filteredVehicles.length)} of {filteredVehicles.length.toLocaleString()} vehicles
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
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                  return (
                    <Button
                      key={pageNum}
                      variant={currentPage === pageNum ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentPage(pageNum)}
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
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
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