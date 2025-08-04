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
    def run_excel_reader(cost_parameters=None):
        """Run excel_reader script to generate pivot tables with optional cost parameters"""
        try:
            script_path = EXCEL_READER_SCRIPT
            
            # Build command with cost parameters if provided
            command = [sys.executable, script_path]
            
            if cost_parameters:
                # Add cost parameters as command line arguments
                if 'freightlinerEvRatioTotal' in cost_parameters:
                    command.extend(['--freightliner-ev-ratio', str(cost_parameters['freightlinerEvRatioTotal'])])
                if 'lightEvRatioTotal' in cost_parameters:
                    command.extend(['--light-ev-ratio', str(cost_parameters['lightEvRatioTotal'])])
                    
                # Heavy vehicle costs
                if 'iceChassisHeavy' in cost_parameters:
                    command.extend(['--ice-chassis-heavy', str(cost_parameters['iceChassisHeavy'])])
                if 'evChassisHeavy' in cost_parameters:
                    command.extend(['--ev-chassis-heavy', str(cost_parameters['evChassisHeavy'])])
                    
                # Van costs
                if 'iceChassisVan' in cost_parameters:
                    command.extend(['--ice-chassis-van', str(cost_parameters['iceChassisVan'])])
                if 'evChassisVan' in cost_parameters:
                    command.extend(['--ev-chassis-van', str(cost_parameters['evChassisVan'])])
                    
                # Car/SUV costs
                if 'iceChassisCar' in cost_parameters:
                    command.extend(['--ice-chassis-car', str(cost_parameters['iceChassisCar'])])
                if 'evChassisCar' in cost_parameters:
                    command.extend(['--ev-chassis-car', str(cost_parameters['evChassisCar'])])
                    
                # Pickup costs
                if 'iceChassisPickup' in cost_parameters:
                    command.extend(['--ice-chassis-pickup', str(cost_parameters['iceChassisPickup'])])
                if 'evChassisPickup' in cost_parameters:
                    command.extend(['--ev-chassis-pickup', str(cost_parameters['evChassisPickup'])])
            
            # Run the script with proper Python path
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()  # Add current directory to Python path
            
            print(f"Running excel_reader with command: {' '.join(command)}")  # Debug log
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Excel reader completed successfully',
                    'output': result.stdout,
                    'parameters_used': cost_parameters or {}
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