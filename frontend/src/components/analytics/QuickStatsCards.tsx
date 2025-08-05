import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Truck, 
  DollarSign, 
  Calendar, 
  MapPin, 
  Building2, 
  BarChart3,
  RefreshCw,
  TrendingUp,
  Package,
  FileText
} from 'lucide-react';
import { analyticsService, QuickStats, QuickStatsResponse } from '@/services/analyticsService';
import { useToast } from '@/hooks/use-toast';

interface QuickStatsCardsProps {
  className?: string;
  pageType?: string; // e.g., 'vehicle-fleet', 'radio-equipment', 'equipment-lifecycle'
  onAnalysisDataLoaded?: (analysisData: any) => void; // Callback to pass analysis data to parent for visualizations
}

export const QuickStatsCards = ({ className = '', pageType, onAnalysisDataLoaded }: QuickStatsCardsProps) => {
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await analyticsService.getQuickStats(pageType);
      
      if (response.success && response.data) {
        setStats(response.data.quick_stats);
        setAnalysisData(response.data.analysis_data);
        
        // Pass analysis data to parent component for visualizations
        if (onAnalysisDataLoaded && response.data.analysis_data) {
          onAnalysisDataLoaded(response.data.analysis_data);
        }
        
        console.log('Analysis data loaded for', pageType, ':', !!response.data.analysis_data);
      } else {
        setError(response.error || 'Failed to load statistics');
        toast({
          title: "Error",
          description: response.error || "Failed to load quick statistics",
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
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className={`grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 ${className}`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                <div className="h-4 bg-muted rounded w-20"></div>
              </CardTitle>
              <div className="h-4 w-4 bg-muted rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-16 mb-2"></div>
              <div className="h-3 bg-muted rounded w-12"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error || !stats) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-destructive">Statistics Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">{error || 'No statistics available'}</p>
          <Button onClick={fetchStats} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const statCards = [
    {
      title: "Total Vehicles",
      value: stats.total_vehicles?.toLocaleString() || "0",
      icon: Truck,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      description: "Fleet vehicles"
    },
    {
      title: "Total Value",
      value: stats.total_value_millions || "$0.0M",
      icon: DollarSign,
      color: "text-green-600",
      bgColor: "bg-green-50",
      description: "Asset value"
    },
    {
      title: "Avg Cost",
      value: stats.avg_cost_formatted || "$0",
      icon: TrendingUp,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      description: "Per vehicle"
    },
    {
      title: "Avg Year",
      value: Math.round(stats.avg_year || 0).toString(),
      icon: Calendar,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      description: "Fleet age"
    },
    {
      title: "Makes",
      value: stats.unique_makes?.toString() || "0",
      icon: Building2,
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
      description: "Manufacturers"
    },
    {
      title: "Locations",
      value: stats.unique_locations?.toString() || "0",
      icon: MapPin,
      color: "text-red-600",
      bgColor: "bg-red-50",
      description: "Sites"
    }
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Fleet Analytics</h3>
          <p className="text-sm text-muted-foreground">
            Real-time statistics across {stats.total_files} data files
          </p>
        </div>
        <Button onClick={fetchStats} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-full ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Additional Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Records</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_records?.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Across all Excel files
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Equipment</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_equipment?.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Total equipment items
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Files</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_files}</div>
            <p className="text-xs text-muted-foreground">
              Excel files analyzed
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default QuickStatsCards;