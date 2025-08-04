import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, AlertTriangle, Truck } from 'lucide-react';

const recentActivities = [
  {
    id: 1,
    type: 'maintenance',
    vehicle: 'Fleet #4521',
    action: 'Scheduled maintenance completed',
    time: '2 hours ago',
    status: 'completed',
    icon: CheckCircle,
  },
  {
    id: 2,
    type: 'upload',
    vehicle: 'Data Import',
    action: 'Vehicle fleet data uploaded',
    time: '4 hours ago',
    status: 'success',
    icon: Truck,
  },
  {
    id: 3,
    type: 'alert',
    vehicle: 'Fleet #3892',
    action: 'Maintenance due in 3 days',
    time: '6 hours ago',
    status: 'warning',
    icon: AlertTriangle,
  },
  {
    id: 4,
    type: 'maintenance',
    vehicle: 'Fleet #2145',
    action: 'Oil change scheduled',
    time: '1 day ago',
    status: 'pending',
    icon: Clock,
  },
  {
    id: 5,
    type: 'completion',
    vehicle: 'Analysis Report',
    action: 'Excel analysis completed',
    time: '1 day ago',
    status: 'completed',
    icon: CheckCircle,
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
    case 'success':
      return 'bg-success text-success-foreground';
    case 'warning':
      return 'bg-warning text-warning-foreground';
    case 'pending':
      return 'bg-muted text-muted-foreground';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return 'Completed';
    case 'success':
      return 'Success';
    case 'warning':
      return 'Warning';
    case 'pending':
      return 'Pending';
    default:
      return 'Unknown';
  }
};

export const RecentActivity: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold text-foreground">
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recentActivities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-accent rounded-lg transition-colors">
            <div className="flex-shrink-0">
              <activity.icon className="w-4 h-4 text-primary mt-0.5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-foreground">{activity.vehicle}</p>
                <Badge variant="secondary" className={`text-xs ${getStatusColor(activity.status)}`}>
                  {getStatusText(activity.status)}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{activity.action}</p>
              <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
            </div>
          </div>
        ))}
        
        <div className="pt-2 border-t border-border">
          <button className="text-sm text-primary hover:underline font-medium">
            View all activity
          </button>
        </div>
      </CardContent>
    </Card>
  );
};