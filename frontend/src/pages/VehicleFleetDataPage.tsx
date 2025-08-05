import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Truck, 
  TrendingUp, 
  BarChart3, 
  PieChart,
  DollarSign,
  Calendar,
  MapPin
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { ExcelDataTable } from '@/components/excel/ExcelDataTable';
import { ColumnStatsDialog } from '@/components/excel/ColumnStatsDialog';
import { QuickStatsCards } from '@/components/analytics/QuickStatsCards';
import { FileAnalytics } from '@/components/analytics/FileAnalytics';
import { 
  excelDataService, 
  ExcelDataResponse, 
  ExcelDataRequest, 
  ExcelColumnStats
} from '@/services/excelDataService';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart as RechartsPieChart, Pie, Cell } from 'recharts';

const COLORS = ['#f97316', '#ea580c', '#c2410c', '#9a3412', '#7c2d12'];

export const VehicleFleetDataPage = () => {
  const [data, setData] = useState<ExcelDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [columnStats, setColumnStats] = useState<ExcelColumnStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null); // Store analysis data for visualizations

  // Handler to receive analysis data from QuickStatsCards
  const handleAnalysisDataLoaded = (data: any) => {
    setAnalysisData(data);
    console.log('Received vehicle fleet analysis data for visualizations:', data);
  };

  // Load initial data
  useEffect(() => {
    handleDataRequest({ page: 1, page_size: 50 });
  }, []);





  const handleDataRequest = async (params: ExcelDataRequest) => {
    setLoading(true);
    setError(null);

    try {
      console.log('Requesting vehicle fleet data with params:', params);
      const response = await excelDataService.getVehicleFleetData(params);
      console.log('Vehicle fleet data response:', response);
      
      if (response.success && response.data) {
        console.log('Setting vehicle fleet data:', response.data);
        setData(response.data);
        toast({
          title: "Data Loaded",
          description: `Loaded ${response.data.pagination?.total_rows?.toLocaleString() || 'N/A'} vehicle records`,
        });
      } else {
        console.error('Failed to load vehicle fleet data:', response.error);
        setError(response.error || 'Failed to load vehicle fleet data');
      }
    } catch (err) {
      console.error('Vehicle fleet data error:', err);
      setError('Failed to load vehicle fleet data: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleViewStats = async (column: string) => {
    setSelectedColumn(column);
    setStatsLoading(true);
    setStatsError(null);
    setColumnStats(null);

    try {
      const response = await excelDataService.getColumnStats('vehicle_fleet_master_data', column);
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



  const calculateSummaryStats = () => {
    if (!data?.data) return null;

    const vehicles = data.data;
    const totalVehicles = vehicles.length;
    const totalCost = vehicles.reduce((sum, v) => sum + (v.Cost || 0), 0);
    const averageCost = totalCost / totalVehicles;
    const avgYear = vehicles.reduce((sum, v) => sum + (v.Year || 0), 0) / totalVehicles;
    const uniqueMakes = new Set(vehicles.map(v => v.Make)).size;
    const uniqueLocations = new Set(vehicles.map(v => v.Location)).size;

    return {
      totalVehicles,
      totalCost,
      averageCost,
      avgYear: Math.round(avgYear),
      uniqueMakes,
      uniqueLocations
    };
  };

  const summaryStats = calculateSummaryStats();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center space-x-2">
            <Truck className="w-6 h-6" />
            <span>Vehicle Fleet Master Data</span>
          </h1>
          <p className="text-muted-foreground">
            Comprehensive vehicle fleet management and analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-primary border-primary">
            <BarChart3 className="w-3 h-3 mr-1" />
            Analytics
          </Badge>
        </div>
      </div>

      {/* Analytics Overview */}
      <QuickStatsCards 
        pageType="vehicle-fleet" 
        onAnalysisDataLoaded={handleAnalysisDataLoaded}
      />

      <Tabs defaultValue="data" className="w-full">
        <TabsList>
          <TabsTrigger value="data">Data Table</TabsTrigger>
          <TabsTrigger value="charts">Charts & Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="data">
          <ExcelDataTable
            data={data}
            loading={loading}
            error={error}
            onRequestData={handleDataRequest}
            title="Vehicle Fleet Data"
            fileKey="vehicle_fleet_master_data"
            onViewStats={handleViewStats}
          />
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          {/* File Analytics */}
          <FileAnalytics 
            fileKey="vehicle_fleet_master_data"
            filename="vehicle_fleet_master_data.xlsx"
          />


          {/* Vehicle Replacement Analysis Visualizations */}
          {analysisData && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Vehicle Replacement Analysis</h3>
              
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Top Categories by 2026 Replacement Cost */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Top Vehicle Categories by Replacement Cost (2026)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.values ? (
                      <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={Object.entries(analysisData.values).map(([category, data]: [string, any]) => ({
                          name: category.replace(/_/g, ' '),
                          cost: data['2026 Replacement Cost (Est.)'] || 0,
                          count: data['2026 Vehicle Count'] || 0
                        })).sort((a, b) => b.cost - a.cost).slice(0, 12)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} fontSize={11} />
                          <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                          <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Replacement Cost']} />
                          <Bar dataKey="cost" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No analysis data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Vehicle Count Distribution */}
                <Card>
                  <CardHeader>
                    <CardTitle>Vehicle Count Distribution (2026)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.values ? (
                      <ResponsiveContainer width="100%" height={350}>
                        <RechartsPieChart>
                          <Pie
                            data={Object.entries(analysisData.values).map(([category, data]: [string, any]) => ({
                              name: category.replace(/_/g, ' '),
                              value: data['2026 Vehicle Count'] || 0
                            })).filter(item => item.value > 0).sort((a, b) => b.value - a.value).slice(0, 8)}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => percent > 5 ? `${name}\n${(percent * 100).toFixed(0)}%` : ''}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(analysisData.values).map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: number) => [`${value} vehicles`, 'Count']} />
                        </RechartsPieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No analysis data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Year-over-Year Trend Analysis */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle>Total Replacement Cost Trend (2026-2035)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.grand_total ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={Object.entries(analysisData.grand_total)
                          .filter(([key]) => key.includes('Replacement Cost'))
                          .map(([key, value]) => ({
                            year: key.split(' ')[0],
                            cost: value as number,
                            count: analysisData.grand_total[key.replace('Replacement Cost (Est.)', 'Vehicle Count')] || 0
                          }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis yAxisId="cost" orientation="left" tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                          <YAxis yAxisId="count" orientation="right" />
                          <Tooltip 
                            formatter={(value: number, name: string) => [
                              name === 'cost' ? `$${value.toLocaleString()}` : `${value} vehicles`,
                              name === 'cost' ? 'Replacement Cost' : 'Vehicle Count'
                            ]} 
                          />
                          <Bar yAxisId="cost" dataKey="cost" fill="#10b981" name="cost" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No trend data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
            )}
        </TabsContent>
      </Tabs>

      {/* Column Statistics Dialog */}
      {selectedColumn && (
        <ColumnStatsDialog
          column={selectedColumn}
          stats={columnStats}
          loading={statsLoading}
          error={statsError}
          trigger={<div />}
        />
      )}
    </div>
  );
};