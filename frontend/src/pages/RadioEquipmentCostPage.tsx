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
  const [analysisData, setAnalysisData] = useState<any>(null); // Store analysis data for visualizations

  // Handler to receive analysis data from QuickStatsCards
  const handleAnalysisDataLoaded = (data: any) => {
    setAnalysisData(data);
    console.log('Received radio equipment analysis data for visualizations:', data);
  };

  useEffect(() => {
    handleDataRequest({ page: 1, page_size: 100 });
  }, []);

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
      <QuickStatsCards 
        pageType="radio-equipment" 
        onAnalysisDataLoaded={handleAnalysisDataLoaded}
      />

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


          {/* Radio Equipment Analysis Visualizations */}
          {analysisData && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Radio Equipment Cost Analysis</h3>
              
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* LOB Spending Comparison */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Total Spending by Line of Business (2026-2035)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.values ? (
                      <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={Object.entries(analysisData.values).map(([lob, data]: [string, any]) => {
                          const totalSpend = Object.entries(data)
                            .filter(([key]) => key.includes('Spend'))
                            .reduce((sum, [_, value]) => sum + (value as number), 0);
                          return {
                            name: lob,
                            totalSpend,
                            avgAnnualSpend: totalSpend / 10
                          };
                        }).sort((a, b) => b.totalSpend - a.totalSpend)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} fontSize={11} />
                          <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                          <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Total Spend']} />
                          <Bar dataKey="totalSpend" fill="#8b5cf6" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No analysis data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Radio Count Distribution */}
                <Card>
                  <CardHeader>
                    <CardTitle>Total Radio Count by LOB</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.values ? (
                      <ResponsiveContainer width="100%" height={350}>
                        <PieChart>
                          <Pie
                            data={Object.entries(analysisData.values).map(([lob, data]: [string, any]) => {
                              const totalCount = Object.entries(data)
                                .filter(([key]) => key.includes('Count'))
                                .reduce((sum, [_, value]) => sum + (value as number), 0);
                              return {
                                name: lob,
                                value: totalCount
                              };
                            }).filter(item => item.value > 0)}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => percent > 8 ? `${name}\n${(percent * 100).toFixed(0)}%` : ''}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(analysisData.values).map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: number) => [`${value} radios`, 'Count']} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No analysis data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Annual Radio Spending Trend */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle>Annual Radio Spending Trend (2026-2035)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.grand_total ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={Object.entries(analysisData.grand_total)
                          .filter(([key]) => key.includes('Radio Spend'))
                          .map(([key, value]) => ({
                            year: key.split(' ')[0],
                            spend: value as number,
                            count: analysisData.grand_total[key.replace('Radio Spend', 'Radio Count')] || 0
                          }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis yAxisId="spend" orientation="left" tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                          <YAxis yAxisId="count" orientation="right" />
                          <Tooltip 
                            formatter={(value: number, name: string) => [
                              name === 'spend' ? `$${value.toLocaleString()}` : `${value} radios`,
                              name === 'spend' ? 'Radio Spend' : 'Radio Count'
                            ]} 
                          />
                          <Line 
                            yAxisId="spend" 
                            type="monotone" 
                            dataKey="spend" 
                            stroke="#f59e0b" 
                            strokeWidth={3}
                            dot={{ fill: '#f59e0b', strokeWidth: 2, r: 5 }}
                            name="spend"
                          />
                          <Line 
                            yAxisId="count" 
                            type="monotone" 
                            dataKey="count" 
                            stroke="#10b981" 
                            strokeWidth={2}
                            dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                            name="count"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No trend data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Cost Efficiency Analysis */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle>Cost Per Radio by LOB (Average 2026-2035)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.values ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={Object.entries(analysisData.values).map(([lob, data]: [string, any]) => {
                          const totalSpend = Object.entries(data)
                            .filter(([key]) => key.includes('Spend'))
                            .reduce((sum, [_, value]) => sum + (value as number), 0);
                          const totalCount = Object.entries(data)
                            .filter(([key]) => key.includes('Count'))
                            .reduce((sum, [_, value]) => sum + (value as number), 0);
                          return {
                            name: lob,
                            costPerRadio: totalCount > 0 ? totalSpend / totalCount : 0,
                            totalCount,
                            totalSpend
                          };
                        }).sort((a, b) => b.costPerRadio - a.costPerRadio)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                          <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                          <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Cost per Radio']} />
                          <Bar dataKey="costPerRadio" fill="#ef4444" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-48 text-muted-foreground">
                        No analysis data available
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