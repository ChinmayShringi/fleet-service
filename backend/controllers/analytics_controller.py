"""
Analytics Controller for handling analytics and summary API requests.
"""

from flask import jsonify, request
from services.analytics_service import AnalyticsService

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
    """Get quick stats for dashboard widgets"""
    try:
        dashboard_summary = analytics_service.get_dashboard_summary()
        
        if not dashboard_summary['success']:
            return jsonify(dashboard_summary), 500
        
        dashboard = dashboard_summary['dashboard']
        
        # Use only cached dashboard data for performance - no expensive analytics calls
        quick_stats = {
            'total_files': dashboard.get('total_files', 0),
            'total_records': dashboard.get('total_records', 0),
            'total_vehicles': dashboard.get('total_vehicles', 0),
            'total_equipment': dashboard.get('total_equipment', 0),
            'total_value': dashboard.get('total_value', 0),
            'total_value_formatted': f"${dashboard.get('total_value', 0):,.0f}",
            'total_value_millions': f"${dashboard.get('total_value', 0) / 1_000_000:.1f}M" if dashboard.get('total_value', 0) > 0 else "$0.0M",
            # Default values for additional stats - can be improved later by including in cache
            'avg_cost': 0,
            'avg_cost_formatted': '$0',
            'avg_year': 0,
            'unique_makes': 0,
            'unique_locations': 0
        }
        
        return jsonify({
            'success': True,
            'quick_stats': quick_stats,
            'dashboard_summary': dashboard
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get quick stats: {str(e)}'
        }), 500