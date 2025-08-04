import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Users, UserPlus, Shield, Activity } from 'lucide-react';
import { apiService, UserStats } from '@/services/apiService';

export const UsersPage: React.FC = () => {
  const [userStats, setUserStats] = useState<UserStats>({
    total_users: 0,
    active_sessions: 0,
    recent_logins: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUserStats = async () => {
      try {
        const response = await apiService.getUserStats();
        if (response.success && response.data) {
          setUserStats(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch user stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserStats();
  }, []);

  const mockUsers = [
    { id: 1, name: 'John Smith', email: 'john.smith@pseg.com', role: 'Fleet Manager', status: 'active', lastLogin: '2 hours ago' },
    { id: 2, name: 'Sarah Johnson', email: 'sarah.johnson@pseg.com', role: 'Analyst', status: 'active', lastLogin: '1 day ago' },
    { id: 3, name: 'Mike Wilson', email: 'mike.wilson@pseg.com', role: 'Technician', status: 'inactive', lastLogin: '3 days ago' },
    { id: 4, name: 'Emily Davis', email: 'emily.davis@pseg.com', role: 'Admin', status: 'active', lastLogin: '5 minutes ago' },
    { id: 5, name: 'Robert Brown', email: 'robert.brown@pseg.com', role: 'Supervisor', status: 'active', lastLogin: '6 hours ago' },
  ];

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'Admin':
        return <Badge variant="destructive">{role}</Badge>;
      case 'Fleet Manager':
        return <Badge variant="default">{role}</Badge>;
      case 'Supervisor':
        return <Badge variant="secondary">{role}</Badge>;
      default:
        return <Badge variant="outline">{role}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    return status === 'active' ? (
      <Badge variant="default" className="bg-success text-success-foreground">Active</Badge>
    ) : (
      <Badge variant="secondary">Inactive</Badge>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-foreground">User Management</h1>
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-16 bg-muted rounded"></div>
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
        <h1 className="text-2xl font-bold text-foreground">User Management</h1>
        <Button>
          <UserPlus className="w-4 h-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* User Statistics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold">{userStats.total_users || mockUsers.length}</p>
              </div>
              <Users className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Sessions</p>
                <p className="text-2xl font-bold">{userStats.active_sessions || 4}</p>
              </div>
              <Activity className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Recent Logins</p>
                <p className="text-2xl font-bold">{userStats.recent_logins || 8}</p>
                <p className="text-xs text-muted-foreground">Last 24 hours</p>
              </div>
              <Shield className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>System Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockUsers.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent transition-colors">
                <div className="flex items-center space-x-4">
                  <Avatar>
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {user.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-medium text-foreground">{user.name}</h3>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <p className="text-xs text-muted-foreground">Last login: {user.lastLogin}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {getRoleBadge(user.role)}
                  {getStatusBadge(user.status)}
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};