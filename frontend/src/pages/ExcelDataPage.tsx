import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Info, Search, TrendingUp } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { ExcelDataTable } from '@/components/excel/ExcelDataTable';
import { ColumnStatsDialog } from '@/components/excel/ColumnStatsDialog';
import { 
  excelDataService, 
  ExcelDataResponse, 
  ExcelDataRequest, 
  ExcelFileInfo,
  ExcelColumnStats
} from '@/services/excelDataService';

export const ExcelDataPage: React.FC = () => {
  const { fileKey } = useParams<{ fileKey: string }>();
  const [data, setData] = useState<ExcelDataResponse | null>(null);
  const [fileInfo, setFileInfo] = useState<ExcelFileInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [columnStats, setColumnStats] = useState<ExcelColumnStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);

  // Load file information
  useEffect(() => {
    if (!fileKey) return;

    const loadFileInfo = async () => {
      try {
        const response = await excelDataService.getFileInfo(fileKey);
        if (response.success && response.data) {
          setFileInfo(response.data.file_info);
        } else {
          setError(response.error || 'Failed to load file information');
        }
      } catch (err) {
        setError('Failed to load file information');
      }
    };

    loadFileInfo();
  }, [fileKey]);

  // Handle data requests
  const handleDataRequest = async (params: ExcelDataRequest) => {
    if (!fileKey) return;

    setLoading(true);
    setError(null);

    try {
      const response = await excelDataService.getFileData(fileKey, params);
      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || 'Failed to load data');
      }
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Handle column statistics
  const handleViewStats = async (column: string) => {
    if (!fileKey) return;

    setSelectedColumn(column);
    setStatsLoading(true);
    setStatsError(null);
    setColumnStats(null);

    try {
      const response = await excelDataService.getColumnStats(fileKey, column);
      if (response.success && response.data) {
        setColumnStats(response.data.column_stats);
      } else {
        setStatsError(response.error || 'Failed to load column statistics');
      }
    } catch (err) {
      setStatsError('Failed to load column statistics');
    } finally {
      setStatsLoading(false);
    }
  };

  // Global search
  const handleGlobalSearch = async (query: string) => {
    try {
      const response = await excelDataService.globalSearch(query, 5);
      if (response.success && response.data) {
        toast({
          title: "Global Search Results",
          description: `Found matches in ${Object.keys(response.data.results).length} files`,
        });
      }
    } catch (err) {
      toast({
        title: "Search Error",
        description: "Failed to perform global search",
        variant: "destructive",
      });
    }
  };

  // Get file display name
  const getFileDisplayName = (key: string): string => {
    const names: Record<string, string> = {
      'vehicle_fleet_master_data': 'Vehicle Fleet Master Data',
      'equipment_lifecycle_reference': 'Equipment Lifecycle Reference',
      'equipment_lifecycle_by_business_unit': 'Equipment Lifecycle by Business Unit',
      'vehicle_replacement_by_category': 'Vehicle Replacement by Category',
      'vehicle_replacement_detailed_forecast': 'Vehicle Replacement Detailed Forecast',
      'radio_equipment_cost_analysis': 'Radio Equipment Cost Analysis',
      'electric_vehicle_budget_analysis': 'Electric Vehicle Budget Analysis',
      'user': 'User Management Data'
    };
    return names[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!fileKey) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-foreground">Excel Data Viewer</h1>
        <Card>
          <CardContent className="p-6">
            <p className="text-muted-foreground">File key not specified in URL.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            {getFileDisplayName(fileKey)}
          </h1>
          {fileInfo && (
            <p className="text-muted-foreground">
              {fileInfo.total_rows.toLocaleString()} rows × {fileInfo.total_columns} columns
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-primary border-primary">
            <FileText className="w-3 h-3 mr-1" />
            Excel Data
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="data" className="w-full">
        <TabsList>
          <TabsTrigger value="data" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Data</span>
          </TabsTrigger>
          <TabsTrigger value="info" className="flex items-center space-x-2">
            <Info className="w-4 h-4" />
            <span>File Info</span>
          </TabsTrigger>
          <TabsTrigger value="search" className="flex items-center space-x-2">
            <Search className="w-4 h-4" />
            <span>Global Search</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="data" className="space-y-4">
          <ExcelDataTable
            data={data}
            loading={loading}
            error={error}
            onRequestData={handleDataRequest}
            title={getFileDisplayName(fileKey)}
            fileKey={fileKey}
            onViewStats={handleViewStats}
          />
          
          {/* Column Statistics Dialog */}
          {selectedColumn && (
            <ColumnStatsDialog
              column={selectedColumn}
              stats={columnStats}
              loading={statsLoading}
              error={statsError}
              trigger={<div />} // Hidden trigger, opened programmatically
            />
          )}
        </TabsContent>

        <TabsContent value="info">
          <Card>
            <CardHeader>
              <CardTitle>File Information</CardTitle>
            </CardHeader>
            <CardContent>
              {fileInfo ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Filename</p>
                      <p className="font-semibold">{fileInfo.filename}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Rows</p>
                      <p className="font-semibold">{fileInfo.total_rows.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Columns</p>
                      <p className="font-semibold">{fileInfo.total_columns}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Sheets</p>
                      <p className="font-semibold">{fileInfo.sheets.length}</p>
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">Available Columns</p>
                    <div className="flex flex-wrap gap-2">
                      {fileInfo.columns.map(column => (
                        <Badge key={column} variant="secondary">
                          {column}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  {fileInfo.sheets.length > 1 && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-2">Available Sheets</p>
                      <div className="flex flex-wrap gap-2">
                        {fileInfo.sheets.map(sheet => (
                          <Badge key={sheet} variant="outline">
                            {sheet}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">Loading file information...</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="search">
          <Card>
            <CardHeader>
              <CardTitle>Global Search</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Search across all available Excel files in the database.
              </p>
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Enter search query..."
                  className="flex-1 px-3 py-2 border rounded-md"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const query = (e.target as HTMLInputElement).value;
                      if (query.trim()) {
                        handleGlobalSearch(query.trim());
                      }
                    }
                  }}
                />
                <Button 
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Enter search query..."]') as HTMLInputElement;
                    if (input?.value.trim()) {
                      handleGlobalSearch(input.value.trim());
                    }
                  }}
                >
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};