import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from '@/hooks/use-toast';
import { apiService, User } from '@/services/apiService';

// User interface now imported from apiService

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, password: string, email: string, role: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('pseg_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        localStorage.removeItem('pseg_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      // Allow admin/admin for demo purposes
      if (username === 'admin' && password === 'admin') {
        const userData: User = {
          id: 1,
          username: 'admin',
          email: 'admin@pseg.com',
          role: 'Admin',
          full_name: 'System Administrator',
          is_active: true
        };
        
        setUser(userData);
        localStorage.setItem('pseg_user', JSON.stringify(userData));
        
        toast({
          title: "Login Successful",
          description: `Welcome back, ${userData.username}!`,
        });
        
        setIsLoading(false);
        return true;
      }

      // Use API service for login
      const response = await apiService.login(username, password);

      if (response.success && response.data) {
        const userData: User = {
          id: response.data.id,
          username: response.data.username,
          email: response.data.email,
          role: response.data.role,
          full_name: response.data.full_name,
          is_active: response.data.is_active
        };
        
        setUser(userData);
        localStorage.setItem('pseg_user', JSON.stringify(userData));
        
        toast({
          title: "Login Successful",
          description: `Welcome back, ${userData.username}!`,
        });
        
        return true;
      } else {
        toast({
          title: "Login Failed",
          description: response.error || "Invalid credentials",
          variant: "destructive",
        });
        return false;
      }
    } catch (error) {
      toast({
        title: "Connection Error",
        description: "Unable to connect to server. Please try again.",
        variant: "destructive",
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, password: string, email: string, role: string = 'user', full_name?: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await apiService.register(username, password, email, full_name, role);
      
      if (response.success) {
        toast({
          title: "Registration Successful",
          description: "Account created successfully. Please login.",
        });
        return true;
      } else {
        toast({
          title: "Registration Failed",
          description: response.error || "Failed to create account",
          variant: "destructive",
        });
        return false;
      }
    } catch (error) {
      toast({
        title: "Registration Error",
        description: "Network error occurred",
        variant: "destructive",
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('pseg_user');
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out.",
    });
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};