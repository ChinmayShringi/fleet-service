"""
Analytics Controller for handling analytics and summary API requests.
"""

from flask import jsonify, request
from services.analytics_service import AnalyticsService
import sys
import os

# Add scripts directory to path so we can import get_analysis
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
try:
    from get_analysis import (
        get_equipment_lifecycle_analysis,
        get_equipment_lifecycle_reference,
        get_radio_equipment_cost_analysis,
        get_vehicle_replacement_by_category_analysis,
        get_vehicle_replacement_detailed_forecast_analysis
    )
except ImportError as e:
    print(f"Warning: Could not import analysis functions: {e}")
    # Define fallback functions
    def get_equipment_lifecycle_analysis():
        return {'success': False, 'error': 'Analysis script not available'}
    def get_equipment_lifecycle_reference():
        return {'success': False, 'error': 'Analysis script not available'}
    def get_radio_equipment_cost_analysis():
        return {'success': False, 'error': 'Analysis script not available'}
    def get_vehicle_replacement_by_category_analysis():
        return {'success': False, 'error': 'Analysis script not available'}
    def get_vehicle_replacement_detailed_forecast_analysis():
        return {'success': False, 'error': 'Analysis script not available'}

# Initialize the analytics service
analytics_service = AnalyticsService()

def get_all_summaries():
    """Get summaries for all Excel files"""
    try:
        result = analytics_service.get_all_file_summaries()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get summaries: {str(e)}'
        }), 500

def get_file_summary(file_key):
    """Get detailed summary for a specific Excel file"""
    try:
        result = analytics_service.get_file_summary(file_key)
        return jsonify({
            'success': True,
            'file_key': file_key,
            'summary': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get file summary: {str(e)}'
        }), 500

def get_dashboard_summary():
    """Get high-level dashboard summary"""
    try:
        result = analytics_service.get_dashboard_summary()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get dashboard summary: {str(e)}'
        }), 500

def get_chart_data():
    """Get chart data for visualizations"""
    try:
        chart_type = request.args.get('type', 'file_overview')
        file_key = request.args.get('file_key')
        
        result = analytics_service.get_chart_data(chart_type, file_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get chart data: {str(e)}'
        }), 500

def get_vehicle_analytics():
    """Get vehicle-specific analytics across all vehicle files"""
    try:
        all_summaries = analytics_service.get_all_file_summaries()
        
        if not all_summaries['success']:
            return jsonify(all_summaries), 500
        
        # Aggregate vehicle data
        vehicle_analytics = {
            'total_vehicles': 0,
            'total_value': 0,
            'unique_makes': set(),
            'unique_locations': set(),
            'unique_types': set(),
            'avg_cost': 0,
            'avg_year': 0,
            'cost_breakdown': {},
            'year_distribution': {},
            'location_distribution': {},
            'make_distribution': {},
            'files_analyzed': []
        }
        
        total_costs = []
        total_years = []
        
        for file_key, file_data in all_summaries['summaries'].items():
            if 'vehicle' in file_key.lower() or 'fleet' in file_key.lower():
                summary = file_data.get('summary', {})
                
                if 'error' not in summary:
                    vehicle_analytics['files_analyzed'].append({
                        'file_key': file_key,
                        'filename': file_data['filename']
                    })
                    
                    # Vehicle stats
                    if 'vehicle_stats' in summary:
                        stats = summary['vehicle_stats']
                        vehicle_analytics['total_vehicles'] += stats.get('total_vehicles', 0)
                        
                        # Track unique values (convert to lists for JSON serialization)
                        if stats.get('unique_makes', 0) > 0:
                            vehicle_analytics['unique_makes'].add(f"{file_key}_makes")
                        if stats.get('unique_locations', 0) > 0:
                            vehicle_analytics['unique_locations'].add(f"{file_key}_locations")
                        if stats.get('unique_types', 0) > 0:
                            vehicle_analytics['unique_types'].add(f"{file_key}_types")
                    
                    # Financial stats
                    if 'financial_stats' in summary:
                        for col, stats in summary['financial_stats'].items():
                            total_value = stats.get('total', 0)
                            vehicle_analytics['total_value'] += total_value
                            
                            avg_cost = stats.get('average', 0)
                            if avg_cost > 0:
                                total_costs.append(avg_cost)
                            
                            vehicle_analytics['cost_breakdown'][f"{file_key}_{col}"] = {
                                'total': total_value,
                                'average': avg_cost,
                                'source_file': file_data['filename']
                            }
                    
                    # Year stats
                    if 'year_stats' in summary:
                        for col, stats in summary['year_stats'].items():
                            avg_year = stats.get('avg_year', 0)
                            if avg_year > 0:
                                total_years.append(avg_year)
                            
                            vehicle_analytics['year_distribution'][f"{file_key}_{col}"] = {
                                'avg_year': avg_year,
                                'oldest': stats.get('oldest', 0),
                                'newest': stats.get('newest', 0),
                                'source_file': file_data['filename']
                            }
        
        # Calculate averages
        if total_costs:
            vehicle_analytics['avg_cost'] = sum(total_costs) / len(total_costs)
        
        if total_years:
            vehicle_analytics['avg_year'] = sum(total_years) / len(total_years)
        
        # Convert sets to counts for JSON serialization
        vehicle_analytics['unique_makes'] = len(vehicle_analytics['unique_makes'])
        vehicle_analytics['unique_locations'] = len(vehicle_analytics['unique_locations'])
        vehicle_analytics['unique_types'] = len(vehicle_analytics['unique_types'])
        
        # Format financial values
        vehicle_analytics['total_value_formatted'] = f"${vehicle_analytics['total_value']:,.0f}"
        vehicle_analytics['total_value_millions'] = f"${vehicle_analytics['total_value'] / 1_000_000:.1f}M"
        vehicle_analytics['avg_cost_formatted'] = f"${vehicle_analytics['avg_cost']:,.0f}"
        
        return jsonify({
            'success': True,
            'analytics': vehicle_analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get vehicle analytics: {str(e)}'
        }), 500

def get_equipment_analytics():
    """Get equipment-specific analytics across all equipment files"""
    try:
        all_summaries = analytics_service.get_all_file_summaries()
        
        if not all_summaries['success']:
            return jsonify(all_summaries), 500
        
        equipment_analytics = {
            'total_equipment': 0,
            'unique_types': 0,
            'unique_locations': 0,
            'unique_manufacturers': 0,
            'avg_lifecycle': 0,
            'lifecycle_distribution': {},
            'files_analyzed': []
        }
        
        total_lifecycles = []
        
        for file_key, file_data in all_summaries['summaries'].items():
            if 'equipment' in file_key.lower():
                summary = file_data.get('summary', {})
                
                if 'error' not in summary:
                    equipment_analytics['files_analyzed'].append({
                        'file_key': file_key,
                        'filename': file_data['filename']
                    })
                    
                    if 'equipment_stats' in summary:
                        stats = summary['equipment_stats']
                        equipment_analytics['total_equipment'] += stats.get('total_equipment', 0)
                        equipment_analytics['unique_types'] += stats.get('unique_types', 0)
                        equipment_analytics['unique_locations'] += stats.get('unique_locations', 0)
                        equipment_analytics['unique_manufacturers'] += stats.get('unique_manufacturers', 0)
                    
                    if 'lifecycle_stats' in summary:
                        for col, stats in summary['lifecycle_stats'].items():
                            avg_lifecycle = stats.get('average_lifecycle', 0)
                            if avg_lifecycle > 0:
                                total_lifecycles.append(avg_lifecycle)
                            
                            equipment_analytics['lifecycle_distribution'][f"{file_key}_{col}"] = {
                                'avg_lifecycle': avg_lifecycle,
                                'total_items': stats.get('total_items', 0),
                                'source_file': file_data['filename']
                            }
        
        if total_lifecycles:
            equipment_analytics['avg_lifecycle'] = sum(total_lifecycles) / len(total_lifecycles)
        
        return jsonify({
            'success': True,
            'analytics': equipment_analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get equipment analytics: {str(e)}'
        }), 500

def get_quick_stats():
    """Get quick stats for dashboard widgets using Excel analysis scripts for specific page"""
    try:
        # Get page parameter from request
        page_type = request.args.get('page', 'default')
        print(f"Fetching quick stats for page type: {page_type}")
        
        # Initialize stats with default values
        quick_stats = {
            'total_files': 1,
            'total_records': 0,
            'total_vehicles': 0,
            'total_equipment': 0,
            'total_value': 0,
            'total_value_formatted': '$0',
            'total_value_millions': '$0.0M',
            'avg_cost': 0,
            'avg_cost_formatted': '$0',
            'avg_year': 0,
            'unique_makes': 0,
            'unique_locations': 0
        }
        
        analysis_result = None
        analysis_type = None
        
        # Call the appropriate analysis function based on page type
        if page_type == 'vehicle-fleet':
            print("Getting vehicle replacement by category analysis for vehicle fleet page...")
            analysis_result = get_vehicle_replacement_by_category_analysis()
            analysis_type = 'vehicle_categories'
            
            if analysis_result['success']:
                categories = analysis_result.get('Categories', [])
                grand_total = analysis_result.get('grand_total', {})
                
                # Extract vehicle counts and costs from grand total
                total_vehicles = 0
                total_value = 0
                for header, value in grand_total.items():
                    if isinstance(value, (int, float)) and value > 0:
                        if 'count' in header.lower() or 'vehicle' in header.lower():
                            total_vehicles += int(value)
                        elif 'cost' in header.lower():
                            total_value += value
                
                avg_cost = total_value / total_vehicles if total_vehicles > 0 else 0
                
                quick_stats.update({
                    'total_records': len(categories),
                    'total_vehicles': total_vehicles,
                    'total_value': total_value,
                    'total_value_formatted': f"${total_value:,.0f}",
                    'total_value_millions': f"${total_value / 1_000_000:.1f}M" if total_value > 0 else "$0.0M",
                    'avg_cost': avg_cost,
                    'avg_cost_formatted': f"${avg_cost:,.0f}",
                    'unique_locations': len(categories)
                })
                
        elif page_type == 'radio-equipment':
            print("Getting radio equipment cost analysis for radio equipment page...")
            analysis_result = get_radio_equipment_cost_analysis()
            analysis_type = 'radio_equipment'
            
            if analysis_result['success']:
                lobs = analysis_result.get('LOB', [])
                grand_total = analysis_result.get('grand_total', {})
                
                # Extract financial data from grand total
                total_value = 0
                radio_count = 0
                for header, value in grand_total.items():
                    if isinstance(value, (int, float)) and value > 0:
                        if 'count' in header.lower():
                            radio_count += int(value)
                        elif 'spend' in header.lower() or 'cost' in header.lower():
                            total_value += value
                
                avg_cost = total_value / radio_count if radio_count > 0 else 0
                
                quick_stats.update({
                    'total_records': len(lobs),
                    'total_equipment': radio_count,
                    'total_value': total_value,
                    'total_value_formatted': f"${total_value:,.0f}",
                    'total_value_millions': f"${total_value / 1_000_000:.1f}M" if total_value > 0 else "$0.0M",
                    'avg_cost': avg_cost,
                    'avg_cost_formatted': f"${avg_cost:,.0f}",
                    'unique_makes': len(lobs)
                })
                
        elif page_type == 'equipment-lifecycle' or page_type == 'electric-vehicle-budget':
            print("Getting equipment lifecycle analysis for equipment page...")
            analysis_result = get_equipment_lifecycle_analysis()
            analysis_type = 'equipment_lifecycle'
            
            if analysis_result['success']:
                total_equipment = analysis_result.get('total_equipment', 0)
                lifecycle_distribution = analysis_result.get('lifecycle_distribution', [])
                
                quick_stats.update({
                    'total_records': len(lifecycle_distribution),
                    'total_equipment': total_equipment,
                    'unique_locations': len(lifecycle_distribution)
                })
                
        elif page_type == 'vehicle-forecast' or page_type == 'vehicle-replacement-forecast':
            print("Getting vehicle replacement detailed forecast analysis for forecast page...")
            analysis_result = get_vehicle_replacement_detailed_forecast_analysis()
            analysis_type = 'vehicle_forecast'
            
            if analysis_result['success']:
                lobs = analysis_result.get('LOB', [])
                data = analysis_result.get('data', {})
                
                # Extract data from LOB totals
                total_vehicles = 0
                total_value = 0
                total_records = 0
                
                for lob, lob_data in data.items():
                    if lob == "Grand Total":
                        continue
                    total_records += len(lob_data)
                    
                    # Extract values from totals
                    for total_type, values in lob_data.items():
                        if isinstance(values, dict):
                            for header, value in values.items():
                                if isinstance(value, (int, float)) and value > 0:
                                    if 'count' in header.lower() or 'vehicle' in header.lower():
                                        total_vehicles += int(value)
                                    elif 'cost' in header.lower():
                                        total_value += value
                
                avg_cost = total_value / total_vehicles if total_vehicles > 0 else 0
                
                quick_stats.update({
                    'total_records': total_records,
                    'total_vehicles': total_vehicles,
                    'total_value': total_value,
                    'total_value_formatted': f"${total_value:,.0f}",
                    'total_value_millions': f"${total_value / 1_000_000:.1f}M" if total_value > 0 else "$0.0M",
                    'avg_cost': avg_cost,
                    'avg_cost_formatted': f"${avg_cost:,.0f}",
                    'unique_makes': len(lobs)
                })
                
        elif page_type == 'equipment-lifecycle-reference':
            print("Getting equipment lifecycle reference analysis for equipment reference page...")
            analysis_result = get_equipment_lifecycle_reference()
            analysis_type = 'equipment_reference'
            
            if analysis_result['success']:
                equipment_data = analysis_result.get('equipment_lifecycle_data', [])
                total_entries = analysis_result.get('total_entries', 0)
                
                # Count unique lifecycle categories
                unique_lifecycles = set()
                for item in equipment_data:
                    if item.get('life_cycle'):
                        unique_lifecycles.add(item['life_cycle'])
                
                quick_stats.update({
                    'total_records': total_entries,
                    'total_equipment': total_entries,
                    'unique_locations': len(unique_lifecycles),
                    'unique_makes': len(unique_lifecycles)
                })
                
        else:
            # Default case - return basic stats
            print(f"No specific analysis for page type '{page_type}', returning default stats")
            analysis_result = {'success': True, 'message': 'Default stats returned'}
            analysis_type = 'default'
        
        print(f"Quick stats calculated for {page_type}:")
        print(f"  Records: {quick_stats['total_records']}")
        print(f"  Vehicles: {quick_stats['total_vehicles']}")
        print(f"  Equipment: {quick_stats['total_equipment']}")
        print(f"  Total Value: {quick_stats['total_value_formatted']}")
        print(f"  Average Cost: {quick_stats['avg_cost_formatted']}")
        
        return jsonify({
            'success': True,
            'quick_stats': quick_stats,
            'page_type': page_type,
            'analysis_type': analysis_type,
            'analysis_success': analysis_result['success'] if analysis_result else False,
            'analysis_data': analysis_result  # Include full analysis data for frontend visualizations
        })
        
    except Exception as e:
        print(f"Error in get_quick_stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get quick stats: {str(e)}'
        }), 500