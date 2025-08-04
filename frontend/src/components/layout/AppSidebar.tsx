import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard,
  Truck,
  Users,
  FileText,
  BarChart3,
  Settings,
  Upload,
  Sun
} from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';

const navigationItems = [
  { title: 'Dashboard', url: '/dashboard', icon: LayoutDashboard },
  { title: 'Fleet Management', url: '/fleet', icon: Truck },
  { title: 'Data Upload', url: '/upload', icon: Upload },
  { title: 'Reports', url: '/reports', icon: FileText },
  { title: 'Analytics', url: '/analytics', icon: BarChart3 },
  { title: 'Users', url: '/users', icon: Users },
  { title: 'Settings', url: '/settings', icon: Settings },
];

export const AppSidebar: React.FC = () => {
  const { state } = useSidebar();
  const { hasRole } = useAuth();
  const location = useLocation();
  const currentPath = location.pathname;
  const collapsed = state === 'collapsed';

  const isActive = (path: string) => currentPath === path || (path === '/dashboard' && currentPath === '/');

  // Filter navigation items based on user role
  const filteredNavigationItems = navigationItems.filter(item => {
    if (item.title === 'Users') {
      return hasRole('Admin'); // Only show Users to Admin
    }
    return true;
  });

  return (
    <Sidebar className={collapsed ? 'w-14' : 'w-64'} collapsible="icon">
      <SidebarContent>
        {/* Logo Section */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Sun className="w-4 h-4 text-primary-foreground" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-lg font-bold text-foreground">PSEG</h1>
                <p className="text-xs text-muted-foreground">Fleet Management</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {filteredNavigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      className={({ isActive: navIsActive }) =>
                        `flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                          isActive(item.url) || navIsActive
                            ? 'bg-primary text-primary-foreground font-medium'
                            : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                        }`
                      }
                    >
                      <item.icon className="w-4 h-4 flex-shrink-0" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};