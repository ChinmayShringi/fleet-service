import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Zap, 
  TrendingUp, 
  BarChart3, 
  DollarSign,
  Calendar,
  Target,
  Battery
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
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'];

export const ElectricVehicleBudgetPage = () => {
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
    console.log('Received equipment lifecycle analysis data for visualizations:', data);
  };

  useEffect(() => {
    handleDataRequest({ page: 1, page_size: 100 });
  }, []);

  const handleDataRequest = async (params: ExcelDataRequest) => {
    setLoading(true);
    setError(null);

    try {
      console.log('Requesting EV budget data with params:', params);
      const response = await excelDataService.getElectricVehicleBudgetData(params);
      console.log('EV budget data response:', response);
      
      if (response.success && response.data) {
        console.log('Setting EV budget data:', response.data);
        console.log('Data structure check:', {
          hasColumns: response.data?.columns !== undefined,
          hasData: response.data?.data !== undefined,
          hasPagination: response.data?.pagination !== undefined,
          columnsLength: response.data?.columns?.length,
          dataLength: response.data?.data?.length
        });
        setData(response.data);
        toast({
          title: "EV Budget Data Loaded",
          description: `Loaded ${response.data.pagination?.total_rows?.toLocaleString() || 'N/A'} budget records`,
        });
      } else {
        console.error('Failed to load EV budget data:', response.error);
        setError(response.error || 'Failed to load electric vehicle budget data');
      }
    } catch (err) {
      console.error('EV budget data error:', err);
      setError('Failed to load electric vehicle budget data: ' + (err instanceof Error ? err.message : 'Unknown error'));
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
      const response = await excelDataService.getColumnStats('electric_vehicle_budget_analysis', column);
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

    const records = data.data;
    const totalRecords = records.length;
    const totalBudget = records.reduce((sum, r) => sum + (parseFloat(r.Budget || r.Cost || 0)), 0);
    const averageBudget = totalBudget / totalRecords;
    const totalEVs = records.reduce((sum, r) => sum + (r.EV_Count || r.Electric_Count || 0), 0);
    const totalFleet = records.reduce((sum, r) => sum + (r.Total_Count || r.Fleet_Size || 1), 0);
    const adoptionRate = (totalEVs / totalFleet) * 100;

    return {
      totalRecords,
      totalBudget,
      averageBudget,
      totalEVs,
      adoptionRate: adoptionRate || 0
    };
  };

  const summaryStats = calculateSummaryStats();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center space-x-2">
            <Zap className="w-6 h-6 text-green-500" />
            <span>Electric Vehicle Budget Analysis</span>
          </h1>
          <p className="text-muted-foreground">
            EV transition budget planning and cost analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-green-500 border-green-500">
            <Battery className="w-3 h-3 mr-1" />
            EV Analytics
          </Badge>
        </div>
      </div>

      {/* Analytics Overview */}
      <QuickStatsCards 
        pageType="electric-vehicle-budget" 
        onAnalysisDataLoaded={handleAnalysisDataLoaded}
      />

      <Tabs defaultValue="data" className="w-full">
        <TabsList>
          <TabsTrigger value="data">Budget Data</TabsTrigger>
          <TabsTrigger value="charts">EV Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="data">
          <ExcelDataTable
            data={data}
            loading={loading}
            error={error}
            onRequestData={handleDataRequest}
            title="Electric Vehicle Budget Data"
            fileKey="electric_vehicle_budget_analysis"
            onViewStats={handleViewStats}
          />
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          {/* File Analytics */}
          <FileAnalytics 
            fileKey="electric_vehicle_budget_analysis"
            filename="electric_vehicle_budget_analysis.xlsx"
          />


          {/* Equipment Lifecycle Analysis Visualizations */}
          {analysisData && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Equipment Lifecycle Analysis</h3>
              
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Equipment Lifecycle Distribution */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Equipment Lifecycle Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.lifecycle_distribution ? (
                      <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={analysisData.lifecycle_distribution.map((item: any) => ({
                          lifecycle: item.lifecycle,
                          count: item.count,
                          percentage: ((item.count / analysisData.total_equipment) * 100).toFixed(1)
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="lifecycle" angle={-45} textAnchor="end" height={100} fontSize={11} />
                          <YAxis />
                          <Tooltip formatter={(value: number, name: string) => [
                            name === 'count' ? `${value} equipment` : value,
                            name === 'count' ? 'Equipment Count' : name
                          ]} />
                          <Bar dataKey="count" fill="#22c55e" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No lifecycle data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Equipment Count Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle>Equipment Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-primary">
                          {analysisData?.total_equipment?.toLocaleString() || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Total Equipment Items</div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="text-sm font-medium">Lifecycle Categories:</div>
                        <div className="text-2xl font-bold text-secondary-foreground">
                          {analysisData?.lifecycle_distribution?.length || 0}
                        </div>
                      </div>

                      {analysisData?.lifecycle_distribution && (
                        <div className="space-y-1">
                          <div className="text-xs text-muted-foreground">Distribution Range:</div>
                          <div className="text-sm">
                            {Math.min(...analysisData.lifecycle_distribution.map((item: any) => item.count))} - {Math.max(...analysisData.lifecycle_distribution.map((item: any) => item.count))} items
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Lifecycle Pie Chart */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle>Equipment Distribution by Lifecycle Category</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.lifecycle_distribution ? (
                      <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                          <Pie
                            data={analysisData.lifecycle_distribution.map((item: any) => ({
                              name: item.lifecycle,
                              value: item.count,
                              percentage: ((item.count / analysisData.total_equipment) * 100).toFixed(1)
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percentage }) => `${name}: ${percentage}%`}
                            outerRadius={120}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {analysisData.lifecycle_distribution.map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: number) => [`${value} equipment`, 'Count']} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No distribution data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Equipment Replacement Priority */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle>Equipment Replacement Priority Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.lifecycle_distribution ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={analysisData.lifecycle_distribution
                          .map((item: any) => ({
                            lifecycle: item.lifecycle,
                            count: item.count,
                            priority: item.lifecycle.includes('20+ years') || item.lifecycle.includes('15-20') ? 'High' :
                                     item.lifecycle.includes('10-15') || item.lifecycle.includes('5-10') ? 'Medium' : 'Low',
                            priorityScore: item.lifecycle.includes('20+ years') ? 4 :
                                          item.lifecycle.includes('15-20') ? 3 :
                                          item.lifecycle.includes('10-15') ? 2 : 1
                          }))
                          .sort((a, b) => b.priorityScore - a.priorityScore)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="lifecycle" angle={-45} textAnchor="end" height={100} />
                          <YAxis />
                          <Tooltip formatter={(value: number) => [`${value} equipment`, 'Count']} />
                          <Bar dataKey="count" fill="#f59e0b" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No priority data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

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