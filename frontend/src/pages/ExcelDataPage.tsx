import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Info, Search, TrendingUp, BarChart3 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { ExcelDataTable } from '@/components/excel/ExcelDataTable';
import { ColumnStatsDialog } from '@/components/excel/ColumnStatsDialog';
import { QuickStatsCards } from '@/components/analytics/QuickStatsCards';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { 
  excelDataService, 
  ExcelDataResponse, 
  ExcelDataRequest, 
  ExcelFileInfo,
  ExcelColumnStats
} from '@/services/excelDataService';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

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
  const [analysisData, setAnalysisData] = useState<any>(null);

  // Define which file keys should show analytics
  const analyticsEnabledFiles = ['equipment_lifecycle_reference', 'vehicle_replacement_detailed_forecast'];
  const showAnalytics = fileKey && analyticsEnabledFiles.includes(fileKey);

  // Handler to receive analysis data from QuickStatsCards
  const handleAnalysisDataLoaded = (data: any) => {
    setAnalysisData(data);
    console.log('Received analysis data for', fileKey, ':', data);
  };

  // Get page type for analytics API
  const getPageType = () => {
    if (fileKey === 'equipment_lifecycle_reference') return 'equipment-lifecycle-reference';
    if (fileKey === 'vehicle_replacement_detailed_forecast') return 'vehicle-replacement-forecast';
    return undefined;
  };

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

      {/* Analytics Overview - only for specific files */}
      {showAnalytics && (
        <QuickStatsCards 
          pageType={getPageType()}
          onAnalysisDataLoaded={handleAnalysisDataLoaded}
        />
      )}

      <Tabs defaultValue="data" className="w-full">
        <TabsList>
          <TabsTrigger value="data" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Data</span>
          </TabsTrigger>
          {showAnalytics && (
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
          )}
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

        {/* Analytics TabsContent - only for specific files */}
        {showAnalytics && (
          <TabsContent value="analytics" className="space-y-6">
            {analysisData && (
              <div className="space-y-6">
                {fileKey === 'equipment_lifecycle_reference' && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Equipment Lifecycle Reference Analysis</h3>
                    <div className="grid gap-6 md:grid-cols-2">
                      {/* Equipment by Lifecycle Chart */}
                      <Card>
                        <CardHeader>
                          <CardTitle>Equipment Distribution by Lifecycle</CardTitle>
                        </CardHeader>
                        <CardContent>
                          {analysisData?.equipment_lifecycle_data ? (
                            <ResponsiveContainer width="100%" height={300}>
                              <BarChart data={analysisData.equipment_lifecycle_data.reduce((acc: any[], item: any) => {
                                const existing = acc.find(x => x.lifecycle === item.life_cycle);
                                if (existing) {
                                  existing.count += 1;
                                } else {
                                  acc.push({ lifecycle: item.life_cycle, count: 1 });
                                }
                                return acc;
                              }, [])}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="lifecycle" angle={-45} textAnchor="end" height={100} />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                              </BarChart>
                            </ResponsiveContainer>
                          ) : (
                            <div className="flex items-center justify-center h-48 text-muted-foreground">
                              No equipment data available
                            </div>
                          )}
                        </CardContent>
                      </Card>

                      {/* Equipment Summary */}
                      <Card>
                        <CardHeader>
                          <CardTitle>Summary Statistics</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="text-center">
                              <div className="text-3xl font-bold text-primary">
                                {analysisData?.total_entries?.toLocaleString() || 0}
                              </div>
                              <div className="text-sm text-muted-foreground">Total Equipment Items</div>
                            </div>
                            <div className="space-y-2">
                              <div className="text-sm font-medium">Unique Lifecycles:</div>
                              <div className="text-2xl font-bold text-secondary-foreground">
                                {analysisData?.equipment_lifecycle_data ? 
                                  new Set(analysisData.equipment_lifecycle_data.map((item: any) => item.life_cycle)).size : 0}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}

                {fileKey === 'vehicle_replacement_detailed_forecast' && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Vehicle Replacement Detailed Forecast Analysis</h3>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {/* LOB Distribution */}
                      <Card className="lg:col-span-2">
                        <CardHeader>
                          <CardTitle>Total Replacement Value by LOB</CardTitle>
                        </CardHeader>
                        <CardContent>
                          {analysisData?.data ? (
                            <ResponsiveContainer width="100%" height={350}>
                              <BarChart data={Object.entries(analysisData.data)
                                .filter(([key]) => key !== "Grand Total")
                                .map(([lob, data]: [string, any]) => {
                                  const totalValue = Object.entries(data)
                                    .filter(([_, values]) => typeof values === 'object' && values !== null)
                                    .reduce((sum, [_, values]: [string, any]) => {
                                      return sum + Object.entries(values)
                                        .filter(([header]) => header.includes('Cost'))
                                        .reduce((costSum, [_, value]) => costSum + (typeof value === 'number' ? value : 0), 0);
                                    }, 0);
                                  return { name: lob, value: totalValue };
                                })
                                .sort((a, b) => b.value - a.value)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                                <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                                <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Total Value']} />
                                <Bar dataKey="value" fill="#10b981" radius={[2, 2, 0, 0]} />
                              </BarChart>
                            </ResponsiveContainer>
                          ) : (
                            <div className="flex items-center justify-center h-48 text-muted-foreground">
                              No forecast data available
                            </div>
                          )}
                        </CardContent>
                      </Card>

                      {/* LOB Summary */}
                      <Card>
                        <CardHeader>
                          <CardTitle>LOB Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="text-center">
                              <div className="text-3xl font-bold text-primary">
                                {analysisData?.LOB?.length || 0}
                              </div>
                              <div className="text-sm text-muted-foreground">Lines of Business</div>
                            </div>
                            <div className="space-y-1 text-xs">
                              {analysisData?.LOB?.slice(0, 4).map((lob: string, index: number) => (
                                <div key={index} className="truncate">{lob}</div>
                              ))}
                              {analysisData?.LOB?.length > 4 && (
                                <div className="text-gray-500">+{analysisData.LOB.length - 4} more</div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {!analysisData && (
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                Loading analytics data...
              </div>
            )}
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};