import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Users, UserPlus, Shield, Activity } from 'lucide-react';
import { apiService, UserStats, User } from '@/services/apiService';
import { toast } from '@/hooks/use-toast';

export const UsersPage: React.FC = () => {
  const [userStats, setUserStats] = useState<UserStats>({
    total_users: 0,
    active_users: 0,
    inactive_users: 0,
  });
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user'
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch user stats and user list in parallel
        const [statsResponse, usersResponse] = await Promise.all([
          apiService.getUserStats(),
          apiService.getAllUsers()
        ]);
        
        if (statsResponse.success && statsResponse.data) {
          setUserStats(statsResponse.data);
        }
        
        if (usersResponse.success && usersResponse.data) {
          const realUsers = usersResponse.data.users || [];
          setUsers(realUsers);
          console.log('Loaded real users from API:', realUsers);
          toast({
            title: "Users Loaded",
            description: `Loaded ${usersResponse.data.count || realUsers.length} real users from database`,
          });
        } else {
          console.error('Failed to load users from API:', usersResponse);
          // Fallback to mock users if API fails
          setUsers(mockUsers.map(user => ({
            id: user.id,
            username: user.name.toLowerCase().replace(' ', '.'),
            email: user.email,
            full_name: user.name,
            role: user.role,
            is_active: user.status === 'active',
            last_login: user.lastLogin
          })));
          
          toast({
            title: "Using Demo Data",
            description: "Could not load users from server, showing demo data",
            variant: "default",
          });
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
        // Use mock data on error
        setUsers(mockUsers.map(user => ({
          id: user.id,
          username: user.name.toLowerCase().replace(' ', '.'),
          email: user.email,
          full_name: user.name,
          role: user.role,
          is_active: user.status === 'active',
          last_login: user.lastLogin
        })));
        
        toast({
          title: "Connection Error",
          description: "Unable to connect to server, showing demo data",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Validate required fields
      if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim()) {
        toast({
          title: "Validation Error",
          description: "Username, email, and password are required",
          variant: "destructive",
        });
        return;
      }

      // Call the register API
      const response = await apiService.register(
        formData.username.trim(),
        formData.password,
        formData.email.trim(),
        formData.full_name.trim() || undefined,
        formData.role
      );

      if (response.success) {
        toast({
          title: "User Created",
          description: `User ${formData.username} has been created successfully`,
        });

        // Reset form and close dialog
        setFormData({
          username: '',
          email: '',
          password: '',
          full_name: '',
          role: 'user'
        });
        setIsDialogOpen(false);

        // Refresh user list and stats
        const [statsResponse, usersResponse] = await Promise.all([
          apiService.getUserStats(),
          apiService.getAllUsers()
        ]);
        
        if (statsResponse.success && statsResponse.data) {
          setUserStats(statsResponse.data);
        }
        
        if (usersResponse.success && usersResponse.data) {
          const realUsers = usersResponse.data.users || [];
          setUsers(realUsers);
        }
        
      } else {
        toast({
          title: "Error Creating User",
          description: response.message || "Failed to create user",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error creating user:', error);
      toast({
        title: "Error",
        description: "An unexpected error occurred while creating the user",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

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
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="w-4 h-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Add New User</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddUser} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username *</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter username"
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter email address"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter password (min 6 characters)"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  minLength={6}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  type="text"
                  placeholder="Enter full name (optional)"
                  value={formData.full_name}
                  onChange={(e) => handleInputChange('full_name', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select value={formData.role} onValueChange={(value) => handleInputChange('role', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                    <SelectItem value="technician">Technician</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="fleet_manager">Fleet Manager</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsDialogOpen(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create User'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
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
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">{userStats.active_users || users.filter(u => u.is_active).length}</p>
              </div>
              <Activity className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Inactive Users</p>
                <p className="text-2xl font-bold">{userStats.inactive_users || users.filter(u => !u.is_active).length}</p>
                <p className="text-xs text-muted-foreground">Disabled accounts</p>
              </div>
              <Shield className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>System Users ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {users.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent transition-colors">
                <div className="flex items-center space-x-4">
                  <Avatar>
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {(user.full_name || user.username).split(' ').map(n => n[0]).join('').toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-medium text-foreground">{user.full_name || user.username}</h3>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <p className="text-xs text-muted-foreground">
                      {user.last_login && !isNaN(Date.parse(user.last_login)) ? `Last login: ${user.last_login}` : 'Never logged in'}
                    </p>
                    {user.created_at && (
                      <p className="text-xs text-muted-foreground">Created: {new Date(user.created_at).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {getRoleBadge(user.role)}
                  {getStatusBadge(user.is_active ? 'active' : 'inactive')}
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