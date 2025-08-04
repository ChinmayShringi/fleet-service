import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Truck, DollarSign, Wrench, TrendingUp, Activity, Users, UserCheck } from 'lucide-react';
import { apiService, UserStats } from '@/services/apiService';
import { FleetOverviewChart } from '@/components/dashboard/FleetOverviewChart';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { useAuth } from '@/contexts/AuthContext';

interface DashboardStats {
  totalVehicles: number;
  monthlyExpenses: number;
  activeMaintenanceRequests: number;
  fleetUtilization: number;
}

interface CombinedStats extends DashboardStats {
  userStats?: UserStats;
}

export const DashboardPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [stats, setStats] = useState<CombinedStats>({
    totalVehicles: 0,
    monthlyExpenses: 0,
    activeMaintenanceRequests: 0,
    fleetUtilization: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch vehicle fleet data and user stats in parallel
        const promises = [apiService.getVehicleFleetData()];
        
        // Add user stats if user is admin
        if (hasRole('Admin')) {
          promises.push(apiService.getUserStats());
        }
        
        const [fleetResponse, userStatsResponse] = await Promise.all(promises);
        
        let fleetStats: DashboardStats = {
          totalVehicles: 6408,
          monthlyExpenses: 45385,
          activeMaintenanceRequests: 127,
          fleetUtilization: 87,
        };
        
        if (fleetResponse.success && fleetResponse.data) {
          // API returns { data: VehicleData[], columns: string[], row_count: number }
          const vehicles = fleetResponse.data.data || [];
          const totalCost = vehicles.reduce((sum, vehicle) => sum + (vehicle.Cost || 0), 0);
          const vehicleCount = fleetResponse.data.row_count || vehicles.length;
          
          fleetStats = {
            totalVehicles: vehicleCount,
            monthlyExpenses: Math.round(totalCost / 12), // Approximate monthly from total cost
            activeMaintenanceRequests: Math.floor(vehicleCount * 0.15), // Simulated
            fleetUtilization: 87, // Simulated percentage
          };
        }
        
        const combinedStats: CombinedStats = {
          ...fleetStats,
          userStats: userStatsResponse?.success ? userStatsResponse.data : undefined
        };
        
        setStats(combinedStats);
      } catch (error) {
        // Fallback to demo data
        setStats({
          totalVehicles: 6408,
          monthlyExpenses: 45385,
          activeMaintenanceRequests: 127,
          fleetUtilization: 87,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [hasRole]);

  const fleetStatCards = [
    {
      title: 'Total Vehicles',
      value: stats.totalVehicles.toLocaleString(),
      icon: Truck,
      description: 'Active fleet vehicles',
      trend: '+2.1%',
    },
    {
      title: 'Monthly Expenses',
      value: `$${stats.monthlyExpenses.toLocaleString()}`,
      icon: DollarSign,
      description: 'Current month spending',
      trend: '+12.5%',
    },
    {
      title: 'Maintenance Requests',
      value: stats.activeMaintenanceRequests.toString(),
      icon: Wrench,
      description: 'Active requests',
      trend: '-3.2%',
    },
    {
      title: 'Fleet Utilization',
      value: `${stats.fleetUtilization}%`,
      icon: TrendingUp,
      description: 'Current utilization rate',
      trend: '+5.4%',
    },
  ];
  
  const userStatCards = stats.userStats ? [
    {
      title: 'Total Users',
      value: stats.userStats.total_users.toString(),
      icon: Users,
      description: 'Registered users',
      trend: null,
    },
    {
      title: 'Active Users',
      value: stats.userStats.active_users.toString(),
      icon: UserCheck,
      description: 'Active accounts',
      trend: null,
    },
  ] : [];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-foreground">Dashboard Overview</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-muted rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Dashboard Overview</h1>
        <Badge variant="outline" className="text-success border-success">
          <Activity className="w-3 h-3 mr-1" />
          System Online
        </Badge>
      </div>

      {/* Fleet Stats Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">Fleet Overview</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {fleetStatCards.map((stat, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                  <span className="text-xs text-success font-medium">{stat.trend}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      
      {/* User Stats Cards (Admin only) */}
      {hasRole('Admin') && userStatCards.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">User Management</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {userStatCards.map((stat, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <stat.icon className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid gap-6 md:grid-cols-2">
        <FleetOverviewChart />
        <RecentActivity />
      </div>
    </div>
  );
};