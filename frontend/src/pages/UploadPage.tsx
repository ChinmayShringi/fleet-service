import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '@/services/apiService';
import { toast } from '@/hooks/use-toast';

interface UploadStatus {
  fileName: string;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  recordsCount?: number;
  error?: string;
}

export const UploadPage: React.FC = () => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (files: FileList | null, type: 'vehicle-fleet' | 'equipment-lifecycle') => {
    if (!files || files.length === 0) return;

    const file = files[0];
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      toast({
        title: "Invalid file type",
        description: "Please upload an Excel file (.xlsx or .xls)",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    const uploadId = Date.now().toString();
    
    setUploadStatus(prev => [...prev, {
      fileName: file.name,
      progress: 0,
      status: 'uploading',
    }]);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadStatus(prev => prev.map(upload => 
          upload.fileName === file.name && upload.status === 'uploading'
            ? { ...upload, progress: Math.min(upload.progress + 10, 90) }
            : upload
        ));
      }, 200);

      let response;
      if (type === 'vehicle-fleet') {
        response = await apiService.uploadVehicleFleet(file);
      } else {
        response = await apiService.uploadEquipmentLifecycle(file);
      }

      clearInterval(progressInterval);

      if (response.success) {
        setUploadStatus(prev => prev.map(upload => 
          upload.fileName === file.name
            ? { 
                ...upload, 
                progress: 100, 
                status: 'success',
                recordsCount: response.data?.records_count
              }
            : upload
        ));
        
        toast({
          title: "Upload successful",
          description: `${file.name} uploaded successfully`,
        });
      } else {
        setUploadStatus(prev => prev.map(upload => 
          upload.fileName === file.name
            ? { 
                ...upload, 
                status: 'error',
                error: response.error || 'Upload failed'
              }
            : upload
        ));
        
        toast({
          title: "Upload failed",
          description: response.error || "Failed to upload file",
          variant: "destructive",
        });
      }
    } catch (error) {
      setUploadStatus(prev => prev.map(upload => 
        upload.fileName === file.name
          ? { 
              ...upload, 
              status: 'error',
              error: 'Network error'
            }
          : upload
      ));
      
      toast({
        title: "Upload error",
        description: "Network error occurred",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Data Upload</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Vehicle Fleet Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5 text-primary" />
              <span>Vehicle Fleet Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Upload Excel files containing vehicle fleet information including equipment, make, model, year, cost, and location data.
            </p>
            
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => handleFileUpload(e.target.files, 'vehicle-fleet')}
                className="hidden"
                id="vehicle-fleet-upload"
                disabled={isUploading}
              />
              <label htmlFor="vehicle-fleet-upload" className="cursor-pointer">
                <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm font-medium">Click to upload or drag and drop</p>
                <p className="text-xs text-muted-foreground">Excel files only (.xlsx, .xls)</p>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Equipment Lifecycle Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5 text-primary" />
              <span>Equipment Lifecycle Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Upload Excel files containing equipment lifecycle information for maintenance scheduling and replacement planning.
            </p>
            
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => handleFileUpload(e.target.files, 'equipment-lifecycle')}
                className="hidden"
                id="equipment-lifecycle-upload"
                disabled={isUploading}
              />
              <label htmlFor="equipment-lifecycle-upload" className="cursor-pointer">
                <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm font-medium">Click to upload or drag and drop</p>
                <p className="text-xs text-muted-foreground">Excel files only (.xlsx, .xls)</p>
              </label>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Status */}
      {uploadStatus.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadStatus.map((upload, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{upload.fileName}</span>
                    <div className="flex items-center space-x-2">
                      {upload.status === 'success' && (
                        <>
                          <Badge variant="default" className="bg-success text-success-foreground">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Success
                          </Badge>
                          {upload.recordsCount && (
                            <span className="text-xs text-muted-foreground">
                              {upload.recordsCount} records
                            </span>
                          )}
                        </>
                      )}
                      {upload.status === 'error' && (
                        <Badge variant="destructive">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          Error
                        </Badge>
                      )}
                      {upload.status === 'uploading' && (
                        <Badge variant="secondary">Uploading...</Badge>
                      )}
                    </div>
                  </div>
                  
                  {upload.status === 'uploading' && (
                    <Progress value={upload.progress} className="w-full" />
                  )}
                  
                  {upload.error && (
                    <p className="text-xs text-destructive">{upload.error}</p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};