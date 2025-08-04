import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  BarChart3, 
  DollarSign,
  Calendar,
  Truck,
  Package,
  MapPin,
  Building2,
  RefreshCw,
  Info,
  TrendingUp
} from 'lucide-react';
import { analyticsService, FileSummary } from '@/services/analyticsService';
import { useToast } from '@/hooks/use-toast';

interface FileAnalyticsProps {
  fileKey: string;
  filename: string;
  className?: string;
}

export const FileAnalytics = ({ fileKey, filename, className = '' }: FileAnalyticsProps) => {
  const [summary, setSummary] = useState<FileSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await analyticsService.getFileSummary(fileKey);
      
      if (response.success && response.data) {
        setSummary(response.data);
        console.log(`File summary for ${fileKey}:`, response.data);
      } else {
        setError(response.error || 'Failed to load file analytics');
        toast({
          title: "Analytics Error",
          description: response.error || "Failed to load file analytics",
          variant: "destructive"
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [fileKey]);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>File Analytics</span>
            <div className="animate-spin">
              <RefreshCw className="w-4 h-4" />
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-muted rounded w-16 mb-2"></div>
                <div className="h-8 bg-muted rounded w-12 mb-1"></div>
                <div className="h-3 bg-muted rounded w-20"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !summary) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-destructive">
            <BarChart3 className="w-5 h-5" />
            <span>File Analytics - Error</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">{error || 'No analytics available'}</p>
          <Button onClick={fetchSummary} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const renderBasicStats = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="text-center">
        <div className="flex items-center justify-center mb-2">
          <FileText className="w-4 h-4 text-blue-600 mr-1" />
          <span className="text-sm font-medium text-muted-foreground">Rows</span>
        </div>
        <div className="text-2xl font-bold">{summary.basic_stats.total_rows.toLocaleString()}</div>
      </div>
      
      <div className="text-center">
        <div className="flex items-center justify-center mb-2">
          <BarChart3 className="w-4 h-4 text-green-600 mr-1" />
          <span className="text-sm font-medium text-muted-foreground">Columns</span>
        </div>
        <div className="text-2xl font-bold">{summary.basic_stats.total_columns}</div>
      </div>
      
      <div className="text-center">
        <div className="flex items-center justify-center mb-2">
          <Info className="w-4 h-4 text-orange-600 mr-1" />
          <span className="text-sm font-medium text-muted-foreground">Size</span>
        </div>
        <div className="text-2xl font-bold">{summary.basic_stats.file_size_mb}MB</div>
      </div>
      
      <div className="text-center">
        <div className="flex items-center justify-center mb-2">
          <FileText className="w-4 h-4 text-purple-600 mr-1" />
          <span className="text-sm font-medium text-muted-foreground">Sheets</span>
        </div>
        <div className="text-2xl font-bold">{summary.basic_stats.sheets.length}</div>
      </div>
    </div>
  );

  const renderVehicleStats = () => {
    if (!summary.vehicle_stats) return null;
    
    const stats = summary.vehicle_stats;
    return (
      <div className="mt-6">
        <h4 className="text-sm font-semibold mb-3 flex items-center">
          <Truck className="w-4 h-4 mr-2 text-blue-600" />
          Vehicle Statistics
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">{stats.total_vehicles.toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Total Vehicles</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{stats.unique_makes}</div>
            <div className="text-xs text-muted-foreground">Makes</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-orange-600">{stats.unique_models}</div>
            <div className="text-xs text-muted-foreground">Models</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">{stats.unique_locations}</div>
            <div className="text-xs text-muted-foreground">Locations</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">{stats.unique_types}</div>
            <div className="text-xs text-muted-foreground">Types</div>
          </div>
        </div>
      </div>
    );
  };

  const renderEquipmentStats = () => {
    if (!summary.equipment_stats) return null;
    
    const stats = summary.equipment_stats;
    return (
      <div className="mt-6">
        <h4 className="text-sm font-semibold mb-3 flex items-center">
          <Package className="w-4 h-4 mr-2 text-green-600" />
          Equipment Statistics
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{stats.total_equipment.toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Total Equipment</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">{stats.unique_types}</div>
            <div className="text-xs text-muted-foreground">Types</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">{stats.unique_locations}</div>
            <div className="text-xs text-muted-foreground">Locations</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">{stats.unique_manufacturers}</div>
            <div className="text-xs text-muted-foreground">Manufacturers</div>
          </div>
        </div>
      </div>
    );
  };

  const renderFinancialStats = () => {
    if (!summary.financial_stats || Object.keys(summary.financial_stats).length === 0) return null;
    
    // Get the first financial column for display
    const [colName, stats] = Object.entries(summary.financial_stats)[0];
    
    return (
      <div className="mt-6">
        <h4 className="text-sm font-semibold mb-3 flex items-center">
          <DollarSign className="w-4 h-4 mr-2 text-green-600" />
          Financial Summary
          <Badge variant="outline" className="ml-2 text-xs">{colName}</Badge>
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">${stats.total.toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Total</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">${Math.round(stats.average).toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Average</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-orange-600">${Math.round(stats.median).toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Median</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">${Math.round(stats.min).toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Min</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">${Math.round(stats.max).toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Max</div>
          </div>
        </div>
      </div>
    );
  };

  const renderYearStats = () => {
    if (!summary.year_stats || Object.keys(summary.year_stats).length === 0) return null;
    
    // Get the first year column for display
    const [colName, stats] = Object.entries(summary.year_stats)[0];
    
    return (
      <div className="mt-6">
        <h4 className="text-sm font-semibold mb-3 flex items-center">
          <Calendar className="w-4 h-4 mr-2 text-blue-600" />
          Year Analysis
          <Badge variant="outline" className="ml-2 text-xs">{colName}</Badge>
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">{Math.round(stats.avg_year)}</div>
            <div className="text-xs text-muted-foreground">Avg Year</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{stats.oldest}</div>
            <div className="text-xs text-muted-foreground">Oldest</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-orange-600">{stats.newest}</div>
            <div className="text-xs text-muted-foreground">Newest</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">{stats.total_count.toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">Total Items</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <span>File Analytics</span>
            <Badge variant="outline">{filename}</Badge>
          </CardTitle>
          <Button onClick={fetchSummary} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Stats */}
        {renderBasicStats()}
        
        {/* Vehicle Stats */}
        {renderVehicleStats()}
        
        {/* Equipment Stats */}
        {renderEquipmentStats()}
        
        {/* Financial Stats */}
        {renderFinancialStats()}
        
        {/* Year Stats */}
        {renderYearStats()}
      </CardContent>
    </Card>
  );
};

export default FileAnalytics;