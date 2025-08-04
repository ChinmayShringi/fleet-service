import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from '@/hooks/use-toast';
import { apiService } from '@/services/apiService';

interface User {
  id: string;
  username: string;
  email: string;
  role: 'Admin' | 'User';
}

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
          id: '1',
          username: 'admin',
          email: 'admin@pseg.com',
          role: 'Admin',
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

      // Try API login for other users
      const response = await fetch('http://localhost:3300/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const userData: User = {
          id: data.user_id || '2',
          username: data.username || username,
          email: data.email || `${username}@pseg.com`,
          role: data.role || 'User',
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
          description: data.message || "Invalid credentials",
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

  const register = async (username: string, password: string, email: string, role: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await apiService.register(username, password, email);
      
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