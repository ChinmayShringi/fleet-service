"""
Fleet Management Script
Dedicated script for handling vehicle fleet data with backend pagination, filtering, and sorting
"""

import pandas as pd
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants.file_constants import get_input_file_safe, get_output_file, ensure_database_directory

class FleetManager:
    """Fleet Management class for handling vehicle data operations"""
    
    def __init__(self):
        """Initialize Fleet Manager"""
        self.fleet_file = 'vehicle_fleet_master_data.xlsx'
        self.data_cache = None
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes cache
        
    def _load_fleet_data(self) -> pd.DataFrame:
        """Load fleet data from Excel file with caching"""
        try:
            # Check if we should use cached data
            if (self.data_cache is not None and 
                self.cache_timestamp is not None and 
                (datetime.now() - self.cache_timestamp).seconds < self.cache_duration):
                return self.data_cache
            
            # Load fresh data from file
            file_path = get_input_file_safe(self.fleet_file)
            
            if not file_path or not os.path.exists(file_path):
                print(f"Fleet file not found at {file_path}, generating demo data")
                return self._generate_demo_data()
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Cache the data
            self.data_cache = df
            self.cache_timestamp = datetime.now()
            
            print(f"Loaded {len(df)} vehicles from {file_path}")
            return df
            
        except Exception as e:
            print(f"Error loading fleet data: {str(e)}")
            return self._generate_demo_data()
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to expected format"""
        # Define column mapping
        column_mapping = {
            'equipment': 'Equipment',
            'equipment_id': 'Equipment',
            'vehicle_id': 'Equipment',
            'make': 'Make',
            'manufacturer': 'Make',
            'model': 'Model',
            'year': 'Year',
            'model_year': 'Year',
            'cost': 'Cost',
            'purchase_cost': 'Cost',
            'value': 'Cost',
            'location': 'Location',
            'site': 'Location',
            'status': 'Status',
            'condition': 'Status',
            'last_maintenance': 'LastMaintenance',
            'maintenance_date': 'LastMaintenance',
            'mileage': 'Mileage',
            'odometer': 'Mileage',
            'fuel_type': 'FuelType',
            'department': 'Department',
            'lob': 'Department',
            'line_of_business': 'Department'
        }
        
        # Rename columns to lowercase for mapping
        df_renamed = df.copy()
        df_renamed.columns = df_renamed.columns.str.lower().str.strip()
        
        # Apply mapping
        for old_col, new_col in column_mapping.items():
            if old_col in df_renamed.columns:
                df_renamed.rename(columns={old_col: new_col}, inplace=True)
        
        # Ensure required columns exist
        required_columns = ['Equipment', 'Make', 'Model', 'Year', 'Cost', 'Location', 'Status']
        for col in required_columns:
            if col not in df_renamed.columns:
                df_renamed[col] = 'Unknown' if col not in ['Year', 'Cost'] else 0
        
        # Clean data types
        if 'Year' in df_renamed.columns:
            df_renamed['Year'] = pd.to_numeric(df_renamed['Year'], errors='coerce').fillna(2020).astype(int)
        
        if 'Cost' in df_renamed.columns:
            df_renamed['Cost'] = pd.to_numeric(df_renamed['Cost'], errors='coerce').fillna(0)
        
        # Clean string columns
        string_columns = ['Equipment', 'Make', 'Model', 'Location', 'Status']
        for col in string_columns:
            if col in df_renamed.columns:
                df_renamed[col] = df_renamed[col].astype(str).str.strip()
                df_renamed[col] = df_renamed[col].replace(['nan', 'NaN', ''], 'Unknown')
        
        return df_renamed
    
    def _generate_demo_data(self) -> pd.DataFrame:
        """Generate demo fleet data for testing"""
        print("Generating demo fleet data...")
        
        import random
        from datetime import datetime, timedelta
        
        # Demo data configuration
        makes = ['Ford', 'Chevrolet', 'Toyota', 'Honda', 'Nissan', 'Ram', 'GMC', 'Jeep']
        models_by_make = {
            'Ford': ['F-150', 'F-250', 'F-350', 'Transit', 'Explorer'],
            'Chevrolet': ['Silverado', 'Colorado', 'Tahoe', 'Express', 'Malibu'],
            'Toyota': ['Camry', 'Prius', 'Tacoma', 'Sienna', 'RAV4'],
            'Honda': ['Accord', 'Civic', 'CR-V', 'Pilot', 'Ridgeline'],
            'Nissan': ['Altima', 'Sentra', 'Frontier', 'NV200', 'Pathfinder'],
            'Ram': ['1500', '2500', '3500', 'ProMaster', 'ProMaster City'],
            'GMC': ['Sierra', 'Canyon', 'Yukon', 'Savana', 'Acadia'],
            'Jeep': ['Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Gladiator']
        }
        
        locations = ['Newark', 'Trenton', 'Camden', 'Paterson', 'Edison', 'Jersey City', 'Elizabeth', 'Woodbridge']
        statuses = ['Active', 'Maintenance', 'Inactive', 'Out of Service']
        fuel_types = ['Gasoline', 'Diesel', 'Electric', 'Hybrid']
        departments = ['Fleet Operations', 'Field Services', 'Emergency Response', 'Administrative', 'Construction']
        
        # Generate data
        data = []
        for i in range(1500):  # Generate 1500 demo vehicles
            make = random.choice(makes)
            model = random.choice(models_by_make[make])
            year = random.randint(2015, 2024)
            
            # Cost based on year and type
            base_cost = random.randint(25000, 85000)
            if year > 2020:
                base_cost *= 1.1
            if 'Electric' in model or random.random() < 0.1:
                base_cost *= 1.3
                fuel_type = 'Electric'
            else:
                fuel_type = random.choice(fuel_types[:-1])  # Exclude Electric for non-EV
            
            vehicle = {
                'Equipment': f'FL-{str(i + 1).zfill(4)}',
                'Make': make,
                'Model': model,
                'Year': year,
                'Cost': round(base_cost, 2),
                'Location': random.choice(locations),
                'Status': random.choice(statuses),
                'FuelType': fuel_type,
                'Department': random.choice(departments),
                'Mileage': random.randint(5000, 150000),
                'LastMaintenance': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
            }
            data.append(vehicle)
        
        df = pd.DataFrame(data)
        
        # Cache demo data
        self.data_cache = df
        self.cache_timestamp = datetime.now()
        
        return df
    
    def get_fleet_data(self, 
                      page: int = 1, 
                      limit: int = 50, 
                      search: str = None,
                      make_filter: str = None,
                      year_filter: int = None,
                      location_filter: str = None,
                      status_filter: str = None,
                      department_filter: str = None,
                      fuel_type_filter: str = None,
                      sort_by: str = 'Equipment',
                      sort_order: str = 'asc') -> Dict[str, Any]:
        """Get paginated and filtered fleet data"""
        
        try:
            # Load data
            df = self._load_fleet_data()
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'No fleet data available',
                    'data': [],
                    'total_count': 0,
                    'page': page,
                    'limit': limit,
                    'total_pages': 0
                }
            
            # Apply filters
            filtered_df = df.copy()
            
            # Search filter
            if search and search.strip():
                search_term = search.strip().lower()
                mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
                filtered_df = df[mask]
            
            # Specific filters
            if make_filter:
                filtered_df = filtered_df[filtered_df['Make'].str.contains(make_filter, case=False, na=False)]
            
            if year_filter:
                filtered_df = filtered_df[filtered_df['Year'] == year_filter]
            
            if location_filter:
                filtered_df = filtered_df[filtered_df['Location'].str.contains(location_filter, case=False, na=False)]
            
            if status_filter:
                filtered_df = filtered_df[filtered_df['Status'].str.contains(status_filter, case=False, na=False)]
            
            if department_filter and 'Department' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Department'].str.contains(department_filter, case=False, na=False)]
            
            if fuel_type_filter and 'FuelType' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['FuelType'].str.contains(fuel_type_filter, case=False, na=False)]
            
            # Sort data
            if sort_by in filtered_df.columns:
                ascending = sort_order.lower() == 'asc'
                filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            
            # Calculate pagination
            total_count = len(filtered_df)
            total_pages = (total_count + limit - 1) // limit
            start_index = (page - 1) * limit
            end_index = start_index + limit
            
            # Get page data
            page_data = filtered_df.iloc[start_index:end_index]
            
            # Convert to records
            records = page_data.to_dict('records')
            
            return {
                'success': True,
                'data': records,
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'columns': list(filtered_df.columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving fleet data: {str(e)}',
                'data': [],
                'total_count': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0
            }
    
    def get_fleet_summary(self) -> Dict[str, Any]:
        """Get fleet summary statistics for charts and overview"""
        
        try:
            df = self._load_fleet_data()
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'No fleet data available for summary'
                }
            
            # Overall statistics
            total_vehicles = len(df)
            total_cost = df['Cost'].sum() if 'Cost' in df.columns else 0
            average_cost = df['Cost'].mean() if 'Cost' in df.columns else 0
            average_year = df['Year'].mean() if 'Year' in df.columns else 0
            
            # Make distribution
            make_distribution = df['Make'].value_counts().to_dict()
            
            # Year distribution
            year_distribution = df['Year'].value_counts().sort_index().to_dict()
            
            # Cost distribution
            cost_ranges = {
                'Under $30k': len(df[df['Cost'] < 30000]),
                '$30k - $50k': len(df[(df['Cost'] >= 30000) & (df['Cost'] < 50000)]),
                '$50k - $75k': len(df[(df['Cost'] >= 50000) & (df['Cost'] < 75000)]),
                'Over $75k': len(df[df['Cost'] >= 75000])
            }
            
            # Location distribution
            location_distribution = df['Location'].value_counts().to_dict()
            
            # Status distribution
            status_distribution = df['Status'].value_counts().to_dict()
            
            # Additional distributions if columns exist
            department_distribution = {}
            fuel_type_distribution = {}
            
            if 'Department' in df.columns:
                department_distribution = df['Department'].value_counts().to_dict()
            
            if 'FuelType' in df.columns:
                fuel_type_distribution = df['FuelType'].value_counts().to_dict()
            
            return {
                'success': True,
                'summary': {
                    'total_vehicles': total_vehicles,
                    'total_cost': total_cost,
                    'average_cost': average_cost,
                    'average_year': average_year,
                    'make_distribution': make_distribution,
                    'year_distribution': year_distribution,
                    'cost_distribution': cost_ranges,
                    'location_distribution': location_distribution,
                    'status_distribution': status_distribution,
                    'department_distribution': department_distribution,
                    'fuel_type_distribution': fuel_type_distribution
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating fleet summary: {str(e)}'
            }
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options for dropdowns"""
        
        try:
            df = self._load_fleet_data()
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'No fleet data available for filters'
                }
            
            options = {
                'makes': sorted(df['Make'].dropna().unique().tolist()),
                'years': sorted(df['Year'].dropna().unique().tolist(), reverse=True),
                'locations': sorted(df['Location'].dropna().unique().tolist()),
                'statuses': sorted(df['Status'].dropna().unique().tolist())
            }
            
            # Add optional columns if they exist
            if 'Department' in df.columns:
                options['departments'] = sorted(df['Department'].dropna().unique().tolist())
            
            if 'FuelType' in df.columns:
                options['fuel_types'] = sorted(df['FuelType'].dropna().unique().tolist())
            
            return {
                'success': True,
                'options': options
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting filter options: {str(e)}'
            }
    
    def export_fleet_data(self, 
                         format: str = 'excel',
                         search: str = None,
                         **filters) -> Dict[str, Any]:
        """Export fleet data in specified format"""
        
        try:
            # Get all data (no pagination for export)
            result = self.get_fleet_data(
                page=1, 
                limit=999999,  # Get all records
                search=search,
                **filters
            )
            
            if not result['success']:
                return result
            
            df = pd.DataFrame(result['data'])
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'No data to export'
                }
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format.lower() == 'excel':
                filename = f'fleet_export_{timestamp}.xlsx'
                filepath = get_output_file(filename)
                df.to_excel(filepath, index=False)
            elif format.lower() == 'csv':
                filename = f'fleet_export_{timestamp}.csv'
                filepath = get_output_file(filename)
                df.to_csv(filepath, index=False)
            else:
                return {
                    'success': False,
                    'message': f'Unsupported export format: {format}'
                }
            
            return {
                'success': True,
                'message': f'Fleet data exported successfully',
                'filename': filename,
                'filepath': filepath,
                'record_count': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error exporting fleet data: {str(e)}'
            }
    
    def invalidate_cache(self):
        """Invalidate the data cache to force fresh data load"""
        self.data_cache = None
        self.cache_timestamp = None
        print("Fleet data cache invalidated")

# Global fleet manager instance
fleet_manager = FleetManager()

# Convenience functions for direct script usage
def get_fleet_data(**kwargs):
    """Get fleet data - convenience function"""
    return fleet_manager.get_fleet_data(**kwargs)

def get_fleet_summary():
    """Get fleet summary - convenience function"""
    return fleet_manager.get_fleet_summary()

def get_filter_options():
    """Get filter options - convenience function"""
    return fleet_manager.get_filter_options()

def export_fleet_data(**kwargs):
    """Export fleet data - convenience function"""
    return fleet_manager.export_fleet_data(**kwargs)

def invalidate_cache():
    """Invalidate cache - convenience function"""
    return fleet_manager.invalidate_cache()

if __name__ == "__main__":
    # Test the fleet manager
    print("Testing Fleet Manager...")
    
    # Test summary
    summary = get_fleet_summary()
    print(f"Summary: {summary['success']}")
    if summary['success']:
        print(f"Total vehicles: {summary['summary']['total_vehicles']}")
    
    # Test paginated data
    data = get_fleet_data(page=1, limit=10)
    print(f"Data: {data['success']}")
    if data['success']:
        print(f"Returned {len(data['data'])} vehicles out of {data['total_count']} total")
    
    # Test filters
    options = get_filter_options()
    print(f"Filter options: {options['success']}")
    if options['success']:
        print(f"Available makes: {len(options['options']['makes'])}")