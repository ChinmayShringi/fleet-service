"""
Analytics Routes for summary and analytics API endpoints.
"""

from flask import Blueprint
from controllers.analytics_controller import (
    get_all_summaries,
    get_file_summary,
    get_dashboard_summary,
    get_chart_data,
    get_vehicle_analytics,
    get_equipment_analytics,
    get_quick_stats
)

# Create the analytics blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Summary endpoints
@analytics_bp.route('/summaries', methods=['GET'])
def summaries():
    """Get summaries for all Excel files
    
    Returns comprehensive summaries including:
    - Basic file statistics
    - Vehicle/equipment counts
    - Financial summaries
    - Unique value counts
    """
    return get_all_summaries()

@analytics_bp.route('/summaries/<file_key>', methods=['GET'])
def file_summary(file_key):
    """Get detailed summary for a specific Excel file
    
    Args:
        file_key: The key identifier for the Excel file
        
    Returns detailed analysis including:
    - File metadata
    - Column statistics
    - Data type analysis
    - Unique value distributions
    """
    return get_file_summary(file_key)

@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Get high-level dashboard summary
    
    Returns aggregated data suitable for dashboard widgets:
    - Total counts across all files
    - Financial summaries
    - File breakdown
    - Key performance indicators
    """
    return get_dashboard_summary()

@analytics_bp.route('/quick-stats', methods=['GET'])
def quick_stats():
    """Get quick stats for dashboard widgets
    
    Returns formatted statistics perfect for dashboard cards:
    - Total Vehicles: 1,234
    - Total Value: $5.2M
    - Avg Cost: $4,500
    - Avg Year: 2018
    - Makes: 15
    - Locations: 8
    """
    return get_quick_stats()

# Specialized analytics endpoints
@analytics_bp.route('/vehicles', methods=['GET'])
def vehicle_analytics():
    """Get comprehensive vehicle analytics
    
    Returns vehicle-specific analytics across all vehicle files:
    - Fleet composition
    - Cost analysis
    - Age distribution
    - Location breakdown
    - Manufacturer analysis
    """
    return get_vehicle_analytics()

@analytics_bp.route('/equipment', methods=['GET'])
def equipment_analytics():
    """Get comprehensive equipment analytics
    
    Returns equipment-specific analytics:
    - Equipment inventory
    - Lifecycle analysis
    - Type distribution
    - Location analysis
    """
    return get_equipment_analytics()

# Chart data endpoints
@analytics_bp.route('/charts', methods=['GET'])
def chart_data():
    """Get chart data for visualizations
    
    Query Parameters:
        type: Chart type (vehicle_by_location, cost_projections, equipment_lifecycle, file_overview)
        file_key: Optional file key to focus on specific file
        
    Returns data formatted for chart libraries:
    - Labels and datasets for Chart.js
    - Ready-to-use visualization data
    """
    return get_chart_data()

@analytics_bp.route('/charts/vehicle-location', methods=['GET'])
def vehicle_location_chart():
    """Get vehicle distribution by location chart data"""
    from flask import request
    request.args = request.args.copy()
    request.args['type'] = 'vehicle_by_location'
    return get_chart_data()

@analytics_bp.route('/charts/cost-projections', methods=['GET'])
def cost_projections_chart():
    """Get cost projections over time chart data"""
    from flask import request
    request.args = request.args.copy()
    request.args['type'] = 'cost_projections'
    return get_chart_data()

@analytics_bp.route('/charts/equipment-lifecycle', methods=['GET'])
def equipment_lifecycle_chart():
    """Get equipment lifecycle analysis chart data"""
    from flask import request
    request.args = request.args.copy()
    request.args['type'] = 'equipment_lifecycle'
    return get_chart_data()

@analytics_bp.route('/charts/file-overview', methods=['GET'])
def file_overview_chart():
    """Get file overview pie chart data"""
    from flask import request
    request.args = request.args.copy()
    request.args['type'] = 'file_overview'
    return get_chart_data()

# Health check
@analytics_bp.route('/health', methods=['GET'])
def health():
    """Health check for analytics service"""
    return {
        'success': True,
        'service': 'Analytics API',
        'status': 'healthy',
        'endpoints': [
            '/api/analytics/summaries - Get all file summaries',
            '/api/analytics/summaries/<file_key> - Get specific file summary',
            '/api/analytics/dashboard - Get dashboard summary',
            '/api/analytics/quick-stats - Get quick stats for widgets',
            '/api/analytics/vehicles - Get vehicle analytics',
            '/api/analytics/equipment - Get equipment analytics',
            '/api/analytics/charts?type=<chart_type> - Get chart data',
            '/api/analytics/charts/vehicle-location - Vehicle location chart',
            '/api/analytics/charts/cost-projections - Cost projection chart',
            '/api/analytics/charts/equipment-lifecycle - Equipment lifecycle chart',
            '/api/analytics/charts/file-overview - File overview chart'
        ]
    }