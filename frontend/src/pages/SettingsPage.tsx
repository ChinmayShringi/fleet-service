import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Settings, Shield, Bell, Database, Activity, CheckCircle } from 'lucide-react';
import { apiService } from '@/services/apiService';
import { toast } from '@/hooks/use-toast';

export const SettingsPage: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<{
    status: string;
    timestamp: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [settings, setSettings] = useState({
    notifications: {
      maintenance_alerts: true,
      cost_warnings: true,
      system_updates: false,
      email_reports: true,
    },
    security: {
      auto_logout: 30,
      two_factor: false,
      password_expiry: 90,
    },
    data: {
      auto_backup: true,
      retention_days: 365,
      export_format: 'xlsx',
    },
  });

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await apiService.healthCheck();
        if (response.success && response.data) {
          setSystemHealth(response.data);
        }
      } catch (error) {
        console.error('Health check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkSystemHealth();
  }, []);

  const handleSettingChange = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value,
      },
    }));
  };

  const saveSettings = () => {
    // Simulate saving settings
    toast({
      title: "Settings saved",
      description: "Your preferences have been updated successfully.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">System Settings</h1>
        {systemHealth && (
          <Badge variant="default" className="bg-success text-success-foreground">
            <CheckCircle className="w-3 h-3 mr-1" />
            System Healthy
          </Badge>
        )}
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-primary" />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="animate-pulse">
              <div className="h-4 bg-muted rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-muted rounded w-1/2"></div>
            </div>
          ) : systemHealth ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Status</span>
                <Badge variant="default" className="bg-success text-success-foreground">
                  {systemHealth.status}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Last Check</span>
                <span className="text-sm text-muted-foreground">
                  {new Date(systemHealth.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Backend URL</span>
                <span className="text-sm text-muted-foreground">http://localhost:3300</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-destructive">Unable to connect to backend service</p>
          )}
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-primary" />
            <span>Notifications</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="maintenance-alerts">Maintenance Alerts</Label>
              <p className="text-sm text-muted-foreground">Get notified about upcoming maintenance</p>
            </div>
            <Switch
              id="maintenance-alerts"
              checked={settings.notifications.maintenance_alerts}
              onCheckedChange={(checked) => handleSettingChange('notifications', 'maintenance_alerts', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="cost-warnings">Cost Warnings</Label>
              <p className="text-sm text-muted-foreground">Alert when costs exceed thresholds</p>
            </div>
            <Switch
              id="cost-warnings"
              checked={settings.notifications.cost_warnings}
              onCheckedChange={(checked) => handleSettingChange('notifications', 'cost_warnings', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="email-reports">Email Reports</Label>
              <p className="text-sm text-muted-foreground">Receive weekly summary reports</p>
            </div>
            <Switch
              id="email-reports"
              checked={settings.notifications.email_reports}
              onCheckedChange={(checked) => handleSettingChange('notifications', 'email_reports', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-primary" />
            <span>Security</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="auto-logout">Auto Logout (minutes)</Label>
            <Input
              id="auto-logout"
              type="number"
              value={settings.security.auto_logout}
              onChange={(e) => handleSettingChange('security', 'auto_logout', parseInt(e.target.value))}
              className="w-32"
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="two-factor">Two-Factor Authentication</Label>
              <p className="text-sm text-muted-foreground">Add extra security to your account</p>
            </div>
            <Switch
              id="two-factor"
              checked={settings.security.two_factor}
              onCheckedChange={(checked) => handleSettingChange('security', 'two_factor', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="grid gap-2">
            <Label htmlFor="password-expiry">Password Expiry (days)</Label>
            <Input
              id="password-expiry"
              type="number"
              value={settings.security.password_expiry}
              onChange={(e) => handleSettingChange('security', 'password_expiry', parseInt(e.target.value))}
              className="w-32"
            />
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-primary" />
            <span>Data Management</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-backup">Automatic Backups</Label>
              <p className="text-sm text-muted-foreground">Backup data daily</p>
            </div>
            <Switch
              id="auto-backup"
              checked={settings.data.auto_backup}
              onCheckedChange={(checked) => handleSettingChange('data', 'auto_backup', checked)}
            />
          </div>
          
          <Separator />
          
          <div className="grid gap-2">
            <Label htmlFor="retention-days">Data Retention (days)</Label>
            <Input
              id="retention-days"
              type="number"
              value={settings.data.retention_days}
              onChange={(e) => handleSettingChange('data', 'retention_days', parseInt(e.target.value))}
              className="w-32"
            />
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={saveSettings} className="w-32">
          <Settings className="w-4 h-4 mr-2" />
          Save Settings
        </Button>
      </div>
    </div>
  );
};