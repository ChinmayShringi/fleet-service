import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { FileText, Download, Play, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '@/services/apiService';
import { toast } from '@/hooks/use-toast';

interface ReportExecution {
  id: string;
  name: string;
  description: string;
  generatedFiles: string[];
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: number;
  executionTime?: number;
  output?: string;
  error?: string;
}

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportExecution[]>([
    {
      id: 'excel-analysis',
      name: 'Excel Analysis Report',
      description: 'Generate comprehensive 10-year vehicle replacement forecasting with electric vehicle transition analysis and radio equipment cost projections',
      generatedFiles: [
        'electric_vehicle_budget_analysis.xlsx',
        'radio_equipment_cost_analysis.xlsx', 
        'vehicle_replacement_detailed_forecast.xlsx',
        'vehicle_replacement_by_category.xlsx'
      ],
      status: 'idle',
      progress: 0,
    },
    {
      id: 'lob-pivot',
      name: 'LOB Pivot Generator',
      description: 'Generate Line of Business equipment lifecycle pivot tables with hierarchical cost analysis by business unit',
      generatedFiles: [
        'equipment_lifecycle_by_business_unit.xlsx'
      ],
      status: 'idle',
      progress: 0,
    },
    {
      id: 'ool-reader',
      name: 'Out-of-Life Analysis',
      description: 'Process out-of-life equipment data and update replacement schedules with detailed lifecycle tracking',
      generatedFiles: [],
      status: 'idle',
      progress: 0,
    },
  ]);

  const executeReport = async (reportId: string) => {
    setReports(prev => prev.map(report => 
      report.id === reportId 
        ? { ...report, status: 'running', progress: 0, error: undefined }
        : report
    ));

    // Simulate progress
    const progressInterval = setInterval(() => {
      setReports(prev => prev.map(report => 
        report.id === reportId && report.status === 'running'
          ? { ...report, progress: Math.min(report.progress + 15, 90) }
          : report
      ));
    }, 500);

    try {
      let response;
      
      switch (reportId) {
        case 'excel-analysis':
          // Get cost parameters from localStorage if available
          const savedParameters = localStorage.getItem('pseg_cost_parameters');
          const costParameters = savedParameters ? JSON.parse(savedParameters) : null;
          console.log('Using cost parameters for Excel analysis:', costParameters);
          response = await apiService.runExcelAnalysis(costParameters);
          break;
        case 'lob-pivot':
          response = await apiService.runLOBPivotGenerator();
          break;
        case 'ool-reader':
          response = await apiService.runOOLReader();
          break;
        default:
          throw new Error('Unknown report type');
      }

      clearInterval(progressInterval);

      if (response.success) {
        const startTime = Date.now();
        setReports(prev => prev.map(report => 
          report.id === reportId
            ? { 
                ...report, 
                status: 'completed', 
                progress: 100,
                executionTime: (Date.now() - startTime) / 1000,
                output: response.data?.output
              }
            : report
        ));
        
        toast({
          title: "Report generated successfully",
          description: response.data?.message || "Report execution completed",
        });
      } else {
        setReports(prev => prev.map(report => 
          report.id === reportId
            ? { 
                ...report, 
                status: 'error',
                error: response.error || 'Execution failed'
              }
            : report
        ));
        
        toast({
          title: "Report generation failed",
          description: response.error || "Failed to execute report",
          variant: "destructive",
        });
      }
    } catch (error) {
      clearInterval(progressInterval);
      
      setReports(prev => prev.map(report => 
        report.id === reportId
          ? { 
              ...report, 
              status: 'error',
              error: 'Network error occurred'
            }
          : report
      ));
      
      toast({
        title: "Execution error",
        description: "Network error occurred",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: ReportExecution['status']) => {
    switch (status) {
      case 'running':
        return (
          <Badge variant="secondary" className="bg-warning text-warning-foreground">
            <Clock className="w-3 h-3 mr-1" />
            Running
          </Badge>
        );
      case 'completed':
        return (
          <Badge variant="default" className="bg-success text-success-foreground">
            <CheckCircle className="w-3 h-3 mr-1" />
            Completed
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="destructive">
            <AlertCircle className="w-3 h-3 mr-1" />
            Error
          </Badge>
        );
      default:
        return (
          <Badge variant="outline">
            Ready
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Reports & Analysis</h1>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => window.location.reload()}
        >
          <Download className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6">
        {reports.map((report) => (
          <Card key={report.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-primary" />
                  <span>{report.name}</span>
                </CardTitle>
                {getStatusBadge(report.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">
                    {report.description}
                  </p>
                  {report.executionTime && (
                    <p className="text-xs text-muted-foreground">
                      Last execution: {report.executionTime.toFixed(2)}s
                    </p>
                  )}
                </div>
                
                <Button
                  onClick={() => executeReport(report.id)}
                  disabled={report.status === 'running'}
                  size="sm"
                >
                  <Play className="w-4 h-4 mr-2" />
                  {report.status === 'running' ? 'Running...' : 'Execute'}
                </Button>
              </div>

              {report.status === 'running' && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{report.progress}%</span>
                  </div>
                  <Progress value={report.progress} />
                </div>
              )}

              {report.error && (
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive">{report.error}</p>
                </div>
              )}

              {report.output && report.status === 'completed' && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Execution Output:</p>
                  <div className="max-h-32 overflow-y-auto p-3 bg-muted rounded-lg">
                    <pre className="text-xs whitespace-pre-wrap text-muted-foreground">
                      {report.output}
                    </pre>
                  </div>
                </div>
              )}

              {report.generatedFiles && report.generatedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    Expected Generated Files:
                    {report.status === 'completed' && (
                      <span className="text-xs text-muted-foreground ml-2">
                        (Check server database/ folder)
                      </span>
                    )}
                  </p>
                  <div className="space-y-1">
                    {report.generatedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-accent rounded">
                        <span className="text-sm">{file}</span>
                        <Badge variant="outline" className="text-xs">
                          Excel Report
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};