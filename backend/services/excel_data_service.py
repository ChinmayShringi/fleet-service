"""
Excel Data Service
Handles reading, filtering, searching, and pagination of Excel files
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
import math
from constants.file_constants import DATABASE_DIR

class ExcelDataService:
    """Service for handling Excel file data operations"""
    
    AVAILABLE_FILES = {
        'vehicle_fleet_master_data': 'vehicle_fleet_master_data.xlsx',
        'equipment_lifecycle_reference': 'equipment_lifecycle_reference.xlsx',
        'equipment_lifecycle_by_business_unit': 'equipment_lifecycle_by_business_unit.xlsx',
        'vehicle_replacement_by_category': 'vehicle_replacement_by_category.xlsx',
        'vehicle_replacement_detailed_forecast': 'vehicle_replacement_detailed_forecast.xlsx',
        'radio_equipment_cost_analysis': 'radio_equipment_cost_analysis.xlsx',
        'electric_vehicle_budget_analysis': 'electric_vehicle_budget_analysis.xlsx',
        'user': 'user.xlsx'
    }
    
    @staticmethod
    def get_available_files() -> Dict[str, str]:
        """Get list of available Excel files"""
        available = {}
        for key, filename in ExcelDataService.AVAILABLE_FILES.items():
            file_path = os.path.join(DATABASE_DIR, filename)
            if os.path.exists(file_path):
                available[key] = filename
        return available
    
    @staticmethod
    def read_excel_file(file_key: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Read Excel file and return DataFrame"""
        if file_key not in ExcelDataService.AVAILABLE_FILES:
            raise ValueError(f"File '{file_key}' not found in available files")
        
        filename = ExcelDataService.AVAILABLE_FILES[file_key]
        file_path = os.path.join(DATABASE_DIR, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Clean column names
            df.columns = df.columns.astype(str)
            
            # Fill NaN values with empty strings for better JSON serialization
            df = df.fillna('')
            
            return df
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    @staticmethod
    def get_file_info(file_key: str) -> Dict[str, Any]:
        """Get information about an Excel file"""
        try:
            df = ExcelDataService.read_excel_file(file_key)
            
            # Get Excel file sheets
            filename = ExcelDataService.AVAILABLE_FILES[file_key]
            file_path = os.path.join(DATABASE_DIR, filename)
            
            try:
                excel_file = pd.ExcelFile(file_path)
                sheets = excel_file.sheet_names
            except:
                sheets = ['Sheet1']  # Default fallback
            
            return {
                'file_key': file_key,
                'filename': filename,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'sheets': sheets,
                'file_path': file_path,
                'file_exists': True
            }
        except Exception as e:
            return {
                'file_key': file_key,
                'filename': ExcelDataService.AVAILABLE_FILES.get(file_key, ''),
                'error': str(e),
                'file_exists': False
            }
    
    @staticmethod
    def filter_and_search_data(
        df: pd.DataFrame,
        search_query: Optional[str] = None,
        column_filters: Optional[Dict[str, Any]] = None,
        value_filters: Optional[Dict[str, Any]] = None,
        sort_column: Optional[str] = None,
        sort_direction: str = 'asc'
    ) -> pd.DataFrame:
        """Apply filters, search, and sorting to DataFrame"""
        
        filtered_df = df.copy()
        
        # Apply column-specific filters
        if column_filters:
            for column, filter_value in column_filters.items():
                if column in filtered_df.columns and filter_value:
                    if isinstance(filter_value, str):
                        # String contains filter (case-insensitive)
                        filtered_df = filtered_df[
                            filtered_df[column].astype(str).str.contains(
                                filter_value, case=False, na=False
                            )
                        ]
                    elif isinstance(filter_value, (int, float)):
                        # Exact numeric match
                        filtered_df = filtered_df[filtered_df[column] == filter_value]
                    elif isinstance(filter_value, list):
                        # Multiple values filter
                        filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
        
        # Apply value filters (range filters for numeric columns)
        if value_filters:
            for column, filter_config in value_filters.items():
                if column in filtered_df.columns:
                    if isinstance(filter_config, dict):
                        min_val = filter_config.get('min')
                        max_val = filter_config.get('max')
                        
                        if min_val is not None:
                            filtered_df = filtered_df[
                                pd.to_numeric(filtered_df[column], errors='coerce') >= min_val
                            ]
                        if max_val is not None:
                            filtered_df = filtered_df[
                                pd.to_numeric(filtered_df[column], errors='coerce') <= max_val
                            ]
        
        # Apply global search query
        if search_query:
            search_mask = pd.Series([False] * len(filtered_df))
            
            for column in filtered_df.columns:
                column_mask = filtered_df[column].astype(str).str.contains(
                    search_query, case=False, na=False
                )
                search_mask = search_mask | column_mask
            
            filtered_df = filtered_df[search_mask]
        
        # Apply sorting
        if sort_column and sort_column in filtered_df.columns:
            ascending = sort_direction.lower() == 'asc'
            filtered_df = filtered_df.sort_values(
                by=sort_column, 
                ascending=ascending,
                na_position='last'
            )
        
        return filtered_df
    
    @staticmethod
    def paginate_data(
        df: pd.DataFrame,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Apply pagination to DataFrame and return data with metadata"""
        
        total_rows = len(df)
        total_pages = math.ceil(total_rows / page_size) if page_size > 0 else 1
        
        # Ensure page is within bounds
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        # Calculate start and end indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get paginated data
        paginated_df = df.iloc[start_idx:end_idx]
        
        # Create pagination metadata
        pagination_info = {
            'current_page': page,
            'page_size': page_size,
            'total_rows': total_rows,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'start_row': start_idx + 1 if total_rows > 0 else 0,
            'end_row': min(end_idx, total_rows)
        }
        
        return paginated_df, pagination_info
    
    @staticmethod
    def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Get statistics for a specific column"""
        if column not in df.columns:
            return {'error': f"Column '{column}' not found"}
        
        col_data = df[column]
        stats = {
            'column_name': column,
            'total_values': len(col_data),
            'non_null_values': col_data.count(),
            'null_values': col_data.isnull().sum(),
            'unique_values': col_data.nunique(),
            'data_type': str(col_data.dtype)
        }
        
        # Add numeric statistics if applicable
        numeric_data = pd.to_numeric(col_data, errors='coerce')
        if not numeric_data.isnull().all():
            stats.update({
                'min_value': numeric_data.min(),
                'max_value': numeric_data.max(),
                'mean_value': numeric_data.mean(),
                'median_value': numeric_data.median(),
                'std_deviation': numeric_data.std()
            })
        
        # Add top values
        try:
            value_counts = col_data.value_counts().head(10)
            stats['top_values'] = [
                {'value': str(val), 'count': int(count)} 
                for val, count in value_counts.items()
            ]
        except:
            stats['top_values'] = []
        
        return stats
    
    @staticmethod
    def get_data_with_filters(
        file_key: str,
        page: int = 1,
        page_size: int = 50,
        search_query: Optional[str] = None,
        column_filters: Optional[Dict[str, Any]] = None,
        value_filters: Optional[Dict[str, Any]] = None,
        sort_column: Optional[str] = None,
        sort_direction: str = 'asc',
        sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get filtered and paginated data from Excel file"""
        
        try:
            # Read the Excel file
            df = ExcelDataService.read_excel_file(file_key, sheet_name)
            
            # Apply filters and search
            filtered_df = ExcelDataService.filter_and_search_data(
                df=df,
                search_query=search_query,
                column_filters=column_filters,
                value_filters=value_filters,
                sort_column=sort_column,
                sort_direction=sort_direction
            )
            
            # Apply pagination
            paginated_df, pagination_info = ExcelDataService.paginate_data(
                filtered_df, page, page_size
            )
            
            # Convert to records for JSON serialization
            data = paginated_df.to_dict('records')
            
            return {
                'success': True,
                'data': data,
                'columns': list(df.columns),
                'pagination': pagination_info,
                'filters_applied': {
                    'search_query': search_query,
                    'column_filters': column_filters,
                    'value_filters': value_filters,
                    'sort_column': sort_column,
                    'sort_direction': sort_direction
                },
                'file_info': {
                    'file_key': file_key,
                    'sheet_name': sheet_name,
                    'total_rows_before_filter': len(df),
                    'total_rows_after_filter': len(filtered_df)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }