"""
File Service
Handles file upload, download, and management operations
"""

import os
import pandas as pd
from werkzeug.utils import secure_filename
from constants.file_constants import DATABASE_DIR, ensure_database_directory

class FileService:
    
    @staticmethod
    def upload_file(file, target_filename):
        """Upload and save file to database directory"""
        try:
            ensure_database_directory()
            
            # Secure the filename
            filename = secure_filename(target_filename)
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            file_path = os.path.join(DATABASE_DIR, filename)
            
            # Save the file
            file.save(file_path)
            
            return {
                'success': True,
                'message': f'File uploaded successfully',
                'file_path': file_path
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Upload failed: {str(e)}'
            }
    
    @staticmethod
    def get_file_data(file_path):
        """Read Excel file and return data"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': 'File not found'
                }
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            return {
                'success': True,
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to read file: {str(e)}'
            }
    
    @staticmethod
    def file_exists(file_path):
        """Check if file exists"""
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat_info = os.stat(file_path)
        return {
            'exists': True,
            'size_mb': round(stat_info.st_size / (1024 * 1024), 2),
            'last_modified': stat_info.st_mtime
        }