import React from 'react';
import { Sun } from 'lucide-react';

interface LoadingScreenProps {
  message?: string;
  overlay?: boolean;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = "Loading...", 
  overlay = false 
}) => {
  return (
    <div className={`
      ${overlay ? 'fixed inset-0 z-50' : 'min-h-screen'} 
      flex items-center justify-center 
      ${overlay ? 'bg-background/80 backdrop-blur-sm' : 'bg-background'}
      animate-fade-in
    `}>
      <div className="text-center space-y-6">
        {/* PSEG Logo with Animation */}
        <div className="flex items-center justify-center space-x-3">
          <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center animate-pulse">
            <Sun className="w-8 h-8 text-primary-foreground animate-spin" style={{ 
              animationDuration: '3s',
              animationTimingFunction: 'ease-in-out'
            }} />
          </div>
          <h1 className="text-4xl font-bold text-foreground opacity-90">PSEG</h1>
        </div>
        
        {/* Loading Dots */}
        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        
        {/* Loading Message */}
        <p className="text-lg text-muted-foreground font-medium">{message}</p>
        
        {/* Progress Bar */}
        <div className="w-64 h-1 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-primary rounded-full animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

export const PageLoader: React.FC = () => {
  return <LoadingScreen message="Loading page..." overlay={true} />;
};