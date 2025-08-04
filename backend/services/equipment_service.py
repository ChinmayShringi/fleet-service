"""
Equipment Service  
Handles equipment reallocation and replacement schedule updates
"""

import sys
import os
import subprocess
from constants.file_constants import (
    DATABASE_DIR,
    OOL_READER_SCRIPT
)

class EquipmentService:
    
    @staticmethod
    def update_replacement_schedule(equipment_ids, new_replacement_year):
        """Update equipment replacement schedule using ool_reader script"""
        try:
            # Validate inputs
            if not equipment_ids or not isinstance(equipment_ids, list):
                return {
                    'success': False,
                    'message': 'Equipment IDs must be provided as a list'
                }
            
            if not isinstance(new_replacement_year, int) or new_replacement_year < 2024 or new_replacement_year > 2050:
                return {
                    'success': False,
                    'message': 'New replacement year must be a valid integer between 2024 and 2050'
                }
            
            print(f"Updating replacement schedule for {len(equipment_ids)} equipment(s) to year {new_replacement_year}")
            print(f"Equipment IDs: {equipment_ids}")
            
            # Import and call the function directly from ool_reader
            try:
                # Add the scripts directory to Python path
                scripts_dir = os.path.dirname(OOL_READER_SCRIPT)
                if scripts_dir not in sys.path:
                    sys.path.insert(0, scripts_dir)
                
                # Import the function
                from scripts.ool_reader import update_equipment_replacement_schedule
                
                # Call the update function
                result = update_equipment_replacement_schedule(equipment_ids, new_replacement_year)
                
                if result is not None:
                    return {
                        'success': True,
                        'message': f'Successfully updated replacement schedules for {len(equipment_ids)} equipment(s)',
                        'equipment_count': len(equipment_ids),
                        'new_replacement_year': new_replacement_year,
                        'equipment_ids': equipment_ids
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Equipment replacement schedule update failed - see logs for details'
                    }
                    
            except ImportError as e:
                return {
                    'success': False,
                    'message': f'Failed to import ool_reader module: {str(e)}'
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Error during equipment replacement schedule update: {str(e)}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update equipment replacement schedule: {str(e)}'
            }
    
    @staticmethod 
    def get_equipment_info(equipment_ids):
        """Get information about specific equipment IDs from the vehicle fleet data"""
        try:
            import pandas as pd
            from constants.file_constants import get_input_file_safe
            
            # Read vehicle fleet data
            data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
            if data_file is None:
                return {
                    'success': False,
                    'message': 'Vehicle fleet master data file not found'
                }
            
            df = pd.read_excel(data_file)
            
            # Find equipment info
            equipment_info = []
            for equipment_id in equipment_ids:
                equipment_row = df[df['Equipment'] == equipment_id]
                if not equipment_row.empty:
                    info = {
                        'equipment_id': equipment_id,
                        'object_type': equipment_row['ObjectType'].iloc[0] if 'ObjectType' in equipment_row.columns else 'Unknown',
                        'equipment_description': equipment_row['Equipment descriptn'].iloc[0] if 'Equipment descriptn' in equipment_row.columns else 'Unknown',
                        'make': equipment_row['Make'].iloc[0] if 'Make' in equipment_row.columns else 'Unknown',
                        'model': equipment_row['Model'].iloc[0] if 'Model' in equipment_row.columns else 'Unknown',
                        'year': equipment_row['Year'].iloc[0] if 'Year' in equipment_row.columns else 'Unknown',
                        'location': equipment_row['Location'].iloc[0] if 'Location' in equipment_row.columns else 'Unknown',
                        'found': True
                    }
                else:
                    info = {
                        'equipment_id': equipment_id,
                        'found': False
                    }
                equipment_info.append(info)
            
            return {
                'success': True,
                'equipment_info': equipment_info,
                'total_requested': len(equipment_ids),
                'found_count': len([info for info in equipment_info if info['found']])
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get equipment info: {str(e)}'
            }