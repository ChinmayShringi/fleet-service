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
  const { hasRole, user } = useAuth();
  const location = useLocation();
  const currentPath = location.pathname;
  const collapsed = state === 'collapsed';

  const isActive = (path: string) => currentPath === path || (path === '/dashboard' && currentPath === '/');

  // Debug: Log user info to help troubleshoot
  console.log('AppSidebar - Current user:', user);
  console.log('AppSidebar - hasRole("Admin"):', hasRole('Admin'));
  console.log('AppSidebar - user?.role:', user?.role);

  // Filter navigation items based on user role
  const filteredNavigationItems = navigationItems.filter(item => {
    if (item.title === 'Users') {
      const isAdmin = hasRole('Admin');
      console.log('AppSidebar - Filtering Users item, isAdmin:', isAdmin);
      // Also try case-insensitive check as fallback
      const isAdminCaseInsensitive = user?.role?.toLowerCase() === 'admin';
      console.log('AppSidebar - Case insensitive admin check:', isAdminCaseInsensitive);
      return isAdmin || isAdminCaseInsensitive; // Only show Users to Admin
    }
    return true;
  });

  console.log('AppSidebar - Filtered navigation items:', filteredNavigationItems.map(i => i.title));

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
          <SidebarGroupLabel className="text-muted-foreground font-medium px-3 mb-2">Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1 px-2">
              {filteredNavigationItems.map((item) => {
                const active = isActive(item.url);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton 
                      asChild 
                      className={`w-full transition-all duration-200 ${
                        active 
                          ? 'bg-primary text-primary-foreground shadow-sm font-medium' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                      }`}
                    >
                      <NavLink
                        to={item.url}
                        className="flex items-center space-x-3 px-3 py-2.5 rounded-lg no-underline"
                      >
                        <item.icon className={`w-4 h-4 flex-shrink-0 ${
                          active ? 'text-primary-foreground' : 'text-inherit'
                        }`} />
                        {!collapsed && (
                          <span className={`text-sm ${
                            active ? 'text-primary-foreground font-medium' : 'text-inherit'
                          }`}>
                            {item.title}
                          </span>
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};