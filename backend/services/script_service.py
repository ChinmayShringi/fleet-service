"""
Script Service  
Handles running the utility scripts for data processing
"""

import sys
import os
import subprocess
from constants.file_constants import (
    DATABASE_DIR,
    EXCEL_READER_SCRIPT,
    LOB_PIVOT_GENERATOR_SCRIPT,
    OOL_READER_SCRIPT
)

class ScriptService:
    
    @staticmethod
    def run_excel_reader():
        """Run excel_reader script to generate pivot tables"""
        try:
            script_path = EXCEL_READER_SCRIPT
            
            # Run the script with proper Python path
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()  # Add current directory to Python path
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Excel reader completed successfully',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'Excel reader failed: {result.stderr}',
                    'output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Excel reader timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to run excel reader: {str(e)}'
            }
    
    @staticmethod
    def run_lob_pivot_generator():
        """Run lob_pivot_generator script"""
        try:
            script_path = LOB_PIVOT_GENERATOR_SCRIPT
            
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()  # Add current directory to Python path
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                env=env
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'LOB pivot generator completed successfully',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'LOB pivot generator failed: {result.stderr}',
                    'output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'LOB pivot generator timed out after 2 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to run LOB pivot generator: {str(e)}'
            }
    
    @staticmethod
    def run_ool_reader():
        """Run ool_reader script to update OOL data"""
        try:
            script_path = OOL_READER_SCRIPT
            
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()  # Add current directory to Python path
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                env=env
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'OOL reader completed successfully',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'OOL reader failed: {result.stderr}',
                    'output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'OOL reader timed out after 2 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to run OOL reader: {str(e)}'
            }