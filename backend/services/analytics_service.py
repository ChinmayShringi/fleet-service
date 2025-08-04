"""
Analytics Service for generating summaries and statistics across all Excel files.
Provides data for dashboard charts, widgets, and analytics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from .excel_data_service import ExcelDataService

class AnalyticsService:
    def __init__(self):
        self.excel_service = ExcelDataService()
        self.data_directory = 'database'
        
    def get_all_file_summaries(self) -> Dict[str, Any]:
        """Get comprehensive summaries for all Excel files"""
        try:
            summaries = {}
            
            # Get all available files
            available_files = self.excel_service.get_available_files()
            
            for file_key, filename in available_files.items():
                try:
                    file_summary = self.get_file_summary(file_key)
                    summaries[file_key] = {
                        'filename': filename,
                        'summary': file_summary,
                        'file_key': file_key
                    }
                except Exception as e:
                    print(f"Error generating summary for {file_key}: {str(e)}")
                    summaries[file_key] = {
                        'filename': filename,
                        'summary': {'error': str(e)},
                        'file_key': file_key
                    }
            
            return {
                'success': True,
                'summaries': summaries,
                'total_files': len(summaries)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate summaries: {str(e)}"
            }
    
    def get_file_summary(self, file_key: str) -> Dict[str, Any]:
        """Generate comprehensive summary for a specific Excel file"""
        try:
            # Load the data
            file_info = self.excel_service.get_file_info(file_key)
            if not file_info['file_exists']:
                return {'error': 'File not found'}
            
            # Read the Excel file
            file_path = file_info['file_path']
            df = pd.read_excel(file_path)
            
            # Basic file statistics
            summary = {
                'basic_stats': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'sheets': file_info.get('sheets', ['Sheet1'])
                }
            }
            
            # Generate specific summaries based on file type
            if 'vehicle' in file_key.lower() or 'fleet' in file_key.lower():
                summary.update(self._generate_vehicle_summary(df))
            elif 'equipment' in file_key.lower():
                summary.update(self._generate_equipment_summary(df))
            elif 'radio' in file_key.lower():
                summary.update(self._generate_radio_summary(df))
            elif 'electric' in file_key.lower() or 'ev' in file_key.lower():
                summary.update(self._generate_ev_summary(df))
            else:
                summary.update(self._generate_generic_summary(df))
            
            return summary
            
        except Exception as e:
            return {'error': f"Failed to generate file summary: {str(e)}"}
    
    def _generate_vehicle_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate vehicle-specific summary statistics"""
        summary = {}
        
        # Vehicle counts and basic stats
        vehicle_stats = {
            'total_vehicles': len(df),
            'unique_makes': self._count_unique_values(df, ['Mfr', 'Make', 'Manufacturer']),
            'unique_models': self._count_unique_values(df, ['Model no.', 'Model', 'Equipment descriptn']),
            'unique_locations': self._count_unique_values(df, ['Location', 'LOB from Location']),
            'unique_types': self._count_unique_values(df, ['ObjectType', 'Vehicle Type'])
        }
        
        # Financial statistics
        financial_cols = [col for col in df.columns if any(term in col.lower() 
                         for term in ['cost', 'value', 'price', 'spend', 'acquisition'])]
        
        if financial_cols:
            financial_stats = {}
            for col in financial_cols:
                if df[col].dtype in ['int64', 'float64']:
                    values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(values) > 0:
                        financial_stats[col] = {
                            'total': float(values.sum()),
                            'average': float(values.mean()),
                            'median': float(values.median()),
                            'min': float(values.min()),
                            'max': float(values.max())
                        }
            
            summary['financial_stats'] = financial_stats
        
        # Year statistics
        year_cols = [col for col in df.columns if 'year' in col.lower() or 'date' in col.lower()]
        if year_cols:
            year_stats = {}
            for col in year_cols:
                try:
                    # Try to extract years from the data
                    years = pd.to_numeric(df[col], errors='coerce').dropna()
                    # Filter reasonable year values
                    years = years[(years >= 1900) & (years <= 2050)]
                    if len(years) > 0:
                        year_stats[col] = {
                            'avg_year': float(years.mean()),
                            'oldest': int(years.min()),
                            'newest': int(years.max()),
                            'total_count': len(years)
                        }
                except:
                    continue
            
            if year_stats:
                summary['year_stats'] = year_stats
        
        summary['vehicle_stats'] = vehicle_stats
        return summary
    
    def _generate_equipment_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate equipment-specific summary statistics"""
        summary = {}
        
        equipment_stats = {
            'total_equipment': len(df),
            'unique_types': self._count_unique_values(df, ['Equipment Type', 'ObjectType', 'Category']),
            'unique_locations': self._count_unique_values(df, ['Location', 'Business Unit', 'Department']),
            'unique_manufacturers': self._count_unique_values(df, ['Manufacturer', 'Mfr', 'Brand'])
        }
        
        # Lifecycle analysis
        lifecycle_cols = [col for col in df.columns if 'lifecycle' in col.lower() or 'life' in col.lower()]
        if lifecycle_cols:
            lifecycle_stats = {}
            for col in lifecycle_cols:
                if df[col].dtype in ['int64', 'float64']:
                    values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(values) > 0:
                        lifecycle_stats[col] = {
                            'average_lifecycle': float(values.mean()),
                            'total_items': len(values)
                        }
            
            if lifecycle_stats:
                summary['lifecycle_stats'] = lifecycle_stats
        
        summary['equipment_stats'] = equipment_stats
        return summary
    
    def _generate_radio_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate radio equipment-specific summary statistics"""
        summary = {}
        
        radio_stats = {
            'total_radios': len(df),
            'unique_lobs': self._count_unique_values(df, ['LOB', 'Line of Business', 'Department'])
        }
        
        # Radio count and spend analysis
        count_cols = [col for col in df.columns if 'count' in col.lower()]
        spend_cols = [col for col in df.columns if 'spend' in col.lower() or 'cost' in col.lower()]
        
        if count_cols:
            total_radio_count = 0
            for col in count_cols:
                values = pd.to_numeric(df[col], errors='coerce').fillna(0)
                total_radio_count += values.sum()
            
            radio_stats['projected_radio_count'] = int(total_radio_count)
        
        if spend_cols:
            total_spend = 0
            for col in spend_cols:
                values = pd.to_numeric(df[col], errors='coerce').fillna(0)
                total_spend += values.sum()
            
            radio_stats['projected_total_spend'] = float(total_spend)
            if radio_stats.get('projected_radio_count', 0) > 0:
                radio_stats['avg_cost_per_radio'] = float(total_spend / radio_stats['projected_radio_count'])
        
        summary['radio_stats'] = radio_stats
        return summary
    
    def _generate_ev_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate electric vehicle-specific summary statistics"""
        summary = {}
        
        ev_stats = {
            'total_vehicle_classes': len(df),
            'unique_classes': self._count_unique_values(df, ['Vehicle Class', 'Class', 'Type'])
        }
        
        # EV count and cost projections
        count_cols = [col for col in df.columns if 'count' in col.lower()]
        cost_cols = [col for col in df.columns if 'cost' in col.lower() or 'replacement' in col.lower()]
        
        if count_cols:
            total_ev_count = 0
            yearly_counts = {}
            for col in count_cols:
                values = pd.to_numeric(df[col], errors='coerce').fillna(0)
                year_match = [year for year in range(2020, 2040) if str(year) in col]
                if year_match:
                    yearly_counts[str(year_match[0])] = int(values.sum())
                total_ev_count += values.sum()
            
            ev_stats['projected_ev_count'] = int(total_ev_count)
            ev_stats['yearly_projections'] = yearly_counts
        
        if cost_cols:
            total_cost = 0
            yearly_costs = {}
            for col in cost_cols:
                values = pd.to_numeric(df[col], errors='coerce').fillna(0)
                year_match = [year for year in range(2020, 2040) if str(year) in col]
                if year_match:
                    yearly_costs[str(year_match[0])] = float(values.sum())
                total_cost += values.sum()
            
            ev_stats['projected_total_cost'] = float(total_cost)
            ev_stats['yearly_cost_projections'] = yearly_costs
            if ev_stats.get('projected_ev_count', 0) > 0:
                ev_stats['avg_cost_per_ev'] = float(total_cost / ev_stats['projected_ev_count'])
        
        summary['ev_stats'] = ev_stats
        return summary
    
    def _generate_generic_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate generic summary for any Excel file"""
        summary = {}
        
        # Column analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        column_stats = {
            'numeric_columns': len(numeric_cols),
            'text_columns': len(text_cols),
            'total_columns': len(df.columns)
        }
        
        # Numeric statistics
        if numeric_cols:
            numeric_stats = {}
            for col in numeric_cols:
                values = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(values) > 0:
                    numeric_stats[col] = {
                        'sum': float(values.sum()),
                        'mean': float(values.mean()),
                        'median': float(values.median()),
                        'std': float(values.std()) if len(values) > 1 else 0,
                        'min': float(values.min()),
                        'max': float(values.max()),
                        'non_null_count': len(values)
                    }
            
            summary['numeric_stats'] = numeric_stats
        
        # Text column unique value counts
        if text_cols:
            text_stats = {}
            for col in text_cols[:10]:  # Limit to first 10 text columns
                unique_count = df[col].nunique()
                text_stats[col] = {
                    'unique_values': unique_count,
                    'non_null_count': df[col].count(),
                    'most_common': df[col].value_counts().head(5).to_dict() if unique_count > 0 else {}
                }
            
            summary['text_stats'] = text_stats
        
        summary['column_stats'] = column_stats
        return summary
    
    def _count_unique_values(self, df: pd.DataFrame, possible_columns: List[str]) -> int:
        """Count unique values in the first matching column"""
        for col in possible_columns:
            if col in df.columns:
                return df[col].nunique()
        return 0
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get high-level summary suitable for dashboard widgets"""
        try:
            all_summaries = self.get_all_file_summaries()
            
            if not all_summaries['success']:
                return all_summaries
            
            dashboard_data = {
                'total_files': all_summaries['total_files'],
                'total_records': 0,
                'total_vehicles': 0,
                'total_equipment': 0,
                'total_value': 0,
                'file_breakdown': {},
                'top_locations': {},
                'top_manufacturers': {},
                'yearly_projections': {}
            }
            
            # Aggregate data across all files
            for file_key, file_data in all_summaries['summaries'].items():
                if 'error' not in file_data['summary']:
                    summary = file_data['summary']
                    
                    # Basic stats
                    if 'basic_stats' in summary:
                        dashboard_data['total_records'] += summary['basic_stats']['total_rows']
                    
                    # Vehicle counts
                    if 'vehicle_stats' in summary:
                        dashboard_data['total_vehicles'] += summary['vehicle_stats']['total_vehicles']
                    
                    # Equipment counts
                    if 'equipment_stats' in summary:
                        dashboard_data['total_equipment'] += summary['equipment_stats']['total_equipment']
                    
                    # Financial totals
                    if 'financial_stats' in summary:
                        for col, stats in summary['financial_stats'].items():
                            dashboard_data['total_value'] += stats.get('total', 0)
                    
                    # File breakdown
                    dashboard_data['file_breakdown'][file_key] = {
                        'filename': file_data['filename'],
                        'records': summary.get('basic_stats', {}).get('total_rows', 0)
                    }
            
            return {
                'success': True,
                'dashboard': dashboard_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate dashboard summary: {str(e)}"
            }
    
    def get_chart_data(self, chart_type: str, file_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate data specifically formatted for different chart types"""
        try:
            if file_key:
                # Chart data for specific file
                summary = self.get_file_summary(file_key)
            else:
                # Chart data across all files
                summary = self.get_dashboard_summary()
            
            chart_data = {}
            
            if chart_type == 'vehicle_by_location':
                chart_data = self._generate_vehicle_location_chart(summary, file_key)
            elif chart_type == 'cost_projections':
                chart_data = self._generate_cost_projection_chart(summary, file_key)
            elif chart_type == 'equipment_lifecycle':
                chart_data = self._generate_equipment_lifecycle_chart(summary, file_key)
            elif chart_type == 'file_overview':
                chart_data = self._generate_file_overview_chart(summary)
            else:
                chart_data = {'error': f'Unknown chart type: {chart_type}'}
            
            return {
                'success': True,
                'chart_type': chart_type,
                'data': chart_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate chart data: {str(e)}"
            }
    
    def _generate_vehicle_location_chart(self, summary: Dict, file_key: Optional[str]) -> Dict[str, Any]:
        """Generate chart data for vehicles by location"""
        # Implementation for location-based vehicle distribution
        return {'labels': [], 'datasets': []}
    
    def _generate_cost_projection_chart(self, summary: Dict, file_key: Optional[str]) -> Dict[str, Any]:
        """Generate chart data for cost projections over time"""
        # Implementation for cost projection charts
        return {'labels': [], 'datasets': []}
    
    def _generate_equipment_lifecycle_chart(self, summary: Dict, file_key: Optional[str]) -> Dict[str, Any]:
        """Generate chart data for equipment lifecycle analysis"""
        # Implementation for equipment lifecycle charts
        return {'labels': [], 'datasets': []}
    
    def _generate_file_overview_chart(self, summary: Dict) -> Dict[str, Any]:
        """Generate chart data for file overview"""
        if 'dashboard' in summary:
            file_breakdown = summary['dashboard'].get('file_breakdown', {})
            return {
                'labels': [data['filename'] for data in file_breakdown.values()],
                'data': [data['records'] for data in file_breakdown.values()],
                'type': 'pie'
            }
        return {'labels': [], 'data': []}