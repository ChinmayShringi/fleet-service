"""
Fleet Routes
API endpoints for fleet management operations
"""

from flask import Blueprint
from controllers.fleet_controller import FleetController

fleet_bp = Blueprint('fleet', __name__, url_prefix='/api/fleet')

# Fleet data endpoints
@fleet_bp.route('/data', methods=['GET'])
def get_fleet_data():
    """Get paginated and filtered fleet data
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 1000)
    - search: Search term for all fields
    - make: Filter by vehicle make
    - year: Filter by vehicle year
    - location: Filter by location
    - status: Filter by status
    - department: Filter by department
    - fuel_type: Filter by fuel type
    - sort_by: Column to sort by (default: Equipment)
    - sort_order: Sort order - 'asc' or 'desc' (default: asc)
    """
    return FleetController.get_fleet_data()

@fleet_bp.route('/summary', methods=['GET'])
def get_fleet_summary():
    """Get fleet summary statistics for charts and dashboard"""
    return FleetController.get_fleet_summary()

@fleet_bp.route('/filters', methods=['GET'])
def get_filter_options():
    """Get available filter options for dropdowns"""
    return FleetController.get_filter_options()

@fleet_bp.route('/export', methods=['GET'])
def export_fleet_data():
    """Export fleet data in specified format
    
    Query Parameters:
    - format: Export format - 'excel' or 'csv' (default: excel)
    - All filter parameters from /data endpoint are supported
    """
    return FleetController.export_fleet_data()

# Vehicle management endpoints
@fleet_bp.route('/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle to the fleet
    
    JSON Body:
    {
        "Equipment": "string (required)",
        "Make": "string (required)",
        "Model": "string (required)", 
        "Year": number (required),
        "Cost": number (required),
        "Location": "string (required)",
        "Status": "string (optional)",
        "Department": "string (optional)",
        "FuelType": "string (optional)",
        "Mileage": number (optional)
    }
    """
    return FleetController.add_vehicle()

@fleet_bp.route('/vehicles/<vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """Update an existing vehicle
    
    Path Parameters:
    - vehicle_id: Vehicle identifier
    
    JSON Body: Partial vehicle data to update
    """
    return FleetController.update_vehicle(vehicle_id)

@fleet_bp.route('/vehicles/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Delete a vehicle from the fleet
    
    Path Parameters:
    - vehicle_id: Vehicle identifier
    """
    return FleetController.delete_vehicle(vehicle_id)

# Cache management
@fleet_bp.route('/cache/refresh', methods=['POST'])
def refresh_cache():
    """Refresh the fleet data cache"""
    return FleetController.refresh_cache()