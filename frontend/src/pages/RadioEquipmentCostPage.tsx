import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Radio, 
  TrendingUp, 
  BarChart3, 
  DollarSign,
  Target,
  Antenna,
  Settings
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

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export const RadioEquipmentCostPage = () => {
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
      console.log('Requesting radio equipment data with params:', params);
      const response = await excelDataService.getRadioEquipmentCostData(params);
      console.log('Radio equipment data response:', response);
      
      if (response.success && response.data) {
        console.log('Setting radio equipment data:', response.data);
        setData(response.data);
        toast({
          title: "Radio Equipment Data Loaded",
          description: `Loaded ${response.data.pagination?.total_rows?.toLocaleString() || 'N/A'} equipment records`,
        });
      } else {
        console.error('Failed to load radio equipment data:', response.error);
        setError(response.error || 'Failed to load radio equipment cost data');
      }
    } catch (err) {
      console.error('Radio equipment data error:', err);
      setError('Failed to load radio equipment cost data: ' + (err instanceof Error ? err.message : 'Unknown error'));
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
      const response = await excelDataService.getColumnStats('radio_equipment_cost_analysis', column);
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
    // Cost trend by year
    const yearlyCosts = records.reduce((acc, record) => {
      const year = record.Year || record.Installation_Year || record.year || 'Unknown';
      const cost = parseFloat(record.Cost || record.Installation_Cost || record.Total_Cost || 0);
      
      if (acc[year]) {
        acc[year] += cost;
      } else {
        acc[year] = cost;
      }
      return acc;
    }, {} as Record<string, number>);

    // Equipment type breakdown
    const equipmentTypes = records.reduce((acc, record) => {
      const type = record.Equipment_Type || record.Type || record.Radio_Type || 'Unknown';
      const cost = parseFloat(record.Cost || record.Installation_Cost || 0);
      
      if (acc[type]) {
        acc[type] += cost;
      } else {
        acc[type] = cost;
      }
      return acc;
    }, {} as Record<string, number>);

    // LOB (Line of Business) breakdown
    const lobBreakdown = records.reduce((acc, record) => {
      const lob = record.LOB || record.Business_Unit || record.Department || 'Unknown';
      const cost = parseFloat(record.Cost || record.Installation_Cost || 0);
      
      if (acc[lob]) {
        acc[lob] += cost;
      } else {
        acc[lob] = cost;
      }
      return acc;
    }, {} as Record<string, number>);

    // Installation cost vs maintenance cost
    const costComparison = records.reduce((acc, record) => {
      const installCost = parseFloat(record.Installation_Cost || record.Initial_Cost || 0);
      const maintCost = parseFloat(record.Maintenance_Cost || record.Annual_Maintenance || 0);
      
      acc.installation += installCost;
      acc.maintenance += maintCost;
      return acc;
    }, { installation: 0, maintenance: 0 });

    setChartData({
      yearlyTrend: Object.entries(yearlyCosts)
        .map(([year, cost]) => ({ year: parseInt(year) || 0, cost }))
        .sort((a, b) => a.year - b.year)
        .slice(0, 15),
      equipmentTypes: Object.entries(equipmentTypes)
        .map(([type, cost]) => ({ type, cost }))
        .slice(0, 8),
      lobBreakdown: Object.entries(lobBreakdown)
        .map(([lob, cost]) => ({ lob, cost }))
        .slice(0, 6),
      costComparison: [
        { category: 'Installation', cost: costComparison.installation },
        { category: 'Maintenance', cost: costComparison.maintenance }
      ]
    });
  };

  const calculateSummaryStats = () => {
    if (!data?.data) return null;

    const records = data.data;
    const totalRecords = records.length;
    const totalCost = records.reduce((sum, r) => sum + (parseFloat(r.Cost || r.Installation_Cost || r.Total_Cost || 0)), 0);
    const averageCost = totalCost / totalRecords;
    const totalInstallCost = records.reduce((sum, r) => sum + (parseFloat(r.Installation_Cost || r.Initial_Cost || 0)), 0);
    const totalMaintCost = records.reduce((sum, r) => sum + (parseFloat(r.Maintenance_Cost || r.Annual_Maintenance || 0)), 0);
    const uniqueTypes = new Set(records.map(r => r.Equipment_Type || r.Type || 'Unknown')).size;

    return {
      totalRecords,
      totalCost,
      averageCost,
      totalInstallCost,
      totalMaintCost,
      uniqueTypes
    };
  };

  const summaryStats = calculateSummaryStats();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center space-x-2">
            <Radio className="w-6 h-6 text-blue-500" />
            <span>Radio Equipment Cost Analysis</span>
          </h1>
          <p className="text-muted-foreground">
            Radio equipment installation and maintenance cost tracking
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-blue-500 border-blue-500">
            <Antenna className="w-3 h-3 mr-1" />
            Radio Analytics
          </Badge>
        </div>
      </div>

      {/* Analytics Overview */}
      <QuickStatsCards />

      <Tabs defaultValue="data" className="w-full">
        <TabsList>
          <TabsTrigger value="data">Equipment Data</TabsTrigger>
          <TabsTrigger value="charts">Cost Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="data">
          <ExcelDataTable
            data={data}
            loading={loading}
            error={error}
            onRequestData={handleDataRequest}
            title="Radio Equipment Cost Data"
            fileKey="radio_equipment_cost_analysis"
            onViewStats={handleViewStats}
          />
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          {/* File Analytics */}
          <FileAnalytics 
            fileKey="radio_equipment_cost_analysis"
            filename="radio_equipment_cost_analysis.xlsx"
          />
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Cost Trend by Year</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData.yearlyTrend || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="year" className="text-xs" />
                      <YAxis className="text-xs" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cost']} />
                      <Line 
                        type="monotone" 
                        dataKey="cost" 
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
                <CardTitle className="text-base">Equipment Types</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData.equipmentTypes || []}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="cost"
                        label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                      >
                        {(chartData.equipmentTypes || []).map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cost']} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Cost by Line of Business</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData.lobBreakdown || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="lob" className="text-xs" angle={-45} textAnchor="end" height={80} />
                      <YAxis className="text-xs" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cost']} />
                      <Bar dataKey="cost" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Installation vs Maintenance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData.costComparison || []}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="category" className="text-xs" />
                      <YAxis className="text-xs" tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                      <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cost']} />
                      <Bar dataKey="cost" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
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