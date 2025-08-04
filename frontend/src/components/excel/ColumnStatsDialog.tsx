import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  BarChart3, 
  Target, 
  Hash,
  Percent,
  Calculator
} from 'lucide-react';
import { ExcelColumnStats } from '@/services/excelDataService';

interface ColumnStatsDialogProps {
  column: string;
  stats: ExcelColumnStats | null;
  loading: boolean;
  error: string | null;
  trigger: React.ReactNode;
}

export const ColumnStatsDialog: React.FC<ColumnStatsDialogProps> = ({
  column,
  stats,
  loading,
  error,
  trigger
}) => {
  const formatNumber = (num: number | undefined) => {
    if (num === undefined || num === null) return 'N/A';
    return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
  };

  const getDataTypeIcon = (dataType: string) => {
    if (dataType.includes('int') || dataType.includes('float')) {
      return <Calculator className="w-4 h-4 text-blue-500" />;
    }
    if (dataType.includes('object') || dataType.includes('string')) {
      return <Hash className="w-4 h-4 text-green-500" />;
    }
    return <Target className="w-4 h-4 text-gray-500" />;
  };

  const getCompleteness = (stats: ExcelColumnStats) => {
    return (stats.non_null_values / stats.total_values) * 100;
  };

  const getUniqueness = (stats: ExcelColumnStats) => {
    return (stats.unique_values / stats.total_values) * 100;
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Column Statistics: {column}</span>
          </DialogTitle>
        </DialogHeader>
        
        {loading && (
          <div className="space-y-4">
            <div className="h-8 bg-muted rounded animate-pulse"></div>
            <div className="h-32 bg-muted rounded animate-pulse"></div>
            <div className="h-24 bg-muted rounded animate-pulse"></div>
          </div>
        )}
        
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-destructive">{error}</p>
          </div>
        )}
        
        {stats && (
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    {getDataTypeIcon(stats.data_type)}
                    <div>
                      <p className="text-xs text-muted-foreground">Data Type</p>
                      <p className="font-semibold">{stats.data_type}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Hash className="w-4 h-4 text-primary" />
                    <div>
                      <p className="text-xs text-muted-foreground">Total Values</p>
                      <p className="font-semibold">{formatNumber(stats.total_values)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Target className="w-4 h-4 text-green-500" />
                    <div>
                      <p className="text-xs text-muted-foreground">Unique Values</p>
                      <p className="font-semibold">{formatNumber(stats.unique_values)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Percent className="w-4 h-4 text-orange-500" />
                    <div>
                      <p className="text-xs text-muted-foreground">Completeness</p>
                      <p className="font-semibold">{getCompleteness(stats).toFixed(1)}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Data Quality Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Data Quality</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Completeness</span>
                    <span>{getCompleteness(stats).toFixed(1)}%</span>
                  </div>
                  <Progress value={getCompleteness(stats)} className="w-full" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatNumber(stats.non_null_values)} non-null values out of {formatNumber(stats.total_values)}
                  </p>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Uniqueness</span>
                    <span>{getUniqueness(stats).toFixed(1)}%</span>
                  </div>
                  <Progress value={getUniqueness(stats)} className="w-full" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatNumber(stats.unique_values)} unique values
                  </p>
                </div>
              </CardContent>
            </Card>
            
            {/* Numeric Statistics (if available) */}
            {(stats.min_value !== undefined || stats.max_value !== undefined) && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center space-x-2">
                    <BarChart3 className="w-4 h-4" />
                    <span>Numeric Statistics</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Minimum</p>
                      <p className="font-semibold text-lg">{formatNumber(stats.min_value)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Maximum</p>
                      <p className="font-semibold text-lg">{formatNumber(stats.max_value)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Mean</p>
                      <p className="font-semibold text-lg">{formatNumber(stats.mean_value)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Median</p>
                      <p className="font-semibold text-lg">{formatNumber(stats.median_value)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Std Deviation</p>
                      <p className="font-semibold text-lg">{formatNumber(stats.std_deviation)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Range</p>
                      <p className="font-semibold text-lg">
                        {stats.min_value !== undefined && stats.max_value !== undefined
                          ? formatNumber(stats.max_value - stats.min_value)
                          : 'N/A'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* Top Values */}
            {stats.top_values.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Most Frequent Values</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {stats.top_values.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{index + 1}</Badge>
                          <span className="font-medium">{item.value}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-muted-foreground">
                            {formatNumber(item.count)} occurrences
                          </span>
                          <Badge variant="secondary">
                            {((item.count / stats.total_values) * 100).toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* Missing Values */}
            {stats.null_values > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-orange-600">Missing Values</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <span>Missing values detected</span>
                    <div className="flex items-center space-x-2">
                      <Badge variant="destructive">
                        {formatNumber(stats.null_values)} missing
                      </Badge>
                      <Badge variant="outline">
                        {((stats.null_values / stats.total_values) * 100).toFixed(1)}% of total
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};