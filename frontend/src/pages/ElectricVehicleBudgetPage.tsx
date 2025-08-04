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
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

export const ElectricVehicleBudgetPage = () => {
  const [data, setData] = useState<ExcelDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [columnStats, setColumnStats] = useState<ExcelColumnStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any>({});

  useEffect(() => {
    handleDataRequest({ page: 1, page_size: 100 });
  }, []);

  useEffect(() => {
    if (data?.data) {
      generateChartData(data.data);
    }
  }, [data]);

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

  const generateChartData = (records: any[]) => {
    // Budget trend by year
    const yearlyBudget = records.reduce((acc, record) => {
      const year = record.Year || record.year || 'Unknown';
      const budget = parseFloat(record.Budget || record.budget || record.Cost || record.cost || 0);
      
      if (acc[year]) {
        acc[year] += budget;
      } else {
        acc[year] = budget;
      }
      return acc;
    }, {} as Record<string, number>);

    // EV adoption rate
    const adoptionData = records.reduce((acc, record) => {
      const year = record.Year || record.year || 'Unknown';
      const evCount = record.EV_Count || record.ev_count || record.Electric_Count || 0;
      const totalCount = record.Total_Count || record.total_count || record.Fleet_Size || 1;
      
      acc[year] = {
        year,
        ev_count: evCount,
        total_count: totalCount,
        adoption_rate: (evCount / totalCount) * 100
      };
      return acc;
    }, {} as Record<string, any>);

    // Category breakdown
    const categoryData = records.reduce((acc, record) => {
      const category = record.Category || record.Vehicle_Type || record.Type || 'Unknown';
      const budget = parseFloat(record.Budget || record.Cost || 0);
      
      if (acc[category]) {
        acc[category] += budget;
      } else {
        acc[category] = budget;
      }
      return acc;
    }, {} as Record<string, number>);

    setChartData({
      yearlyTrend: Object.entries(yearlyBudget)
        .map(([year, budget]) => ({ year: parseInt(year) || 0, budget }))
        .sort((a, b) => a.year - b.year)
        .slice(0, 15),
      adoptionTrend: Object.values(adoptionData)
        .sort((a: any, b: any) => a.year - b.year)
        .slice(0, 15),
      categoryBreakdown: Object.entries(categoryData)
        .map(([category, budget]) => ({ category, budget }))
        .slice(0, 10)
    });
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
      <QuickStatsCards />

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
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Budget Trend by Year</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData.yearlyTrend || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="year" className="text-xs" />
                      <YAxis className="text-xs" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Budget']} />
                      <Line 
                        type="monotone" 
                        dataKey="budget" 
                        stroke="hsl(var(--primary))" 
                        strokeWidth={2}
                        dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">EV Adoption Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData.adoptionTrend || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="year" className="text-xs" />
                      <YAxis className="text-xs" tickFormatter={(value) => `${value}%`} />
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Adoption Rate']} />
                      <Line 
                        type="monotone" 
                        dataKey="adoption_rate" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="text-base">Budget by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData.categoryBreakdown || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="category" className="text-xs" angle={-45} textAnchor="end" height={100} />
                      <YAxis className="text-xs" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Budget']} />
                      <Bar dataKey="budget" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
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