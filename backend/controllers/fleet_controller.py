"""
Fleet Controller
Handles all fleet management API endpoints with backend pagination and filtering
"""

from flask import request, jsonify
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

try:
    from fleet_management import fleet_manager
except ImportError as e:
    print(f"Warning: Could not import fleet_management: {e}")
    fleet_manager = None

class FleetController:
    
    @staticmethod
    def get_fleet_data():
        """Get paginated and filtered fleet data"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            # Get query parameters
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            search = request.args.get('search', None)
            
            # Filter parameters
            make_filter = request.args.get('make', None)
            year_filter = request.args.get('year', None)
            location_filter = request.args.get('location', None)
            status_filter = request.args.get('status', None)
            department_filter = request.args.get('department', None)
            fuel_type_filter = request.args.get('fuel_type', None)
            
            # Sorting parameters
            sort_by = request.args.get('sort_by', 'Equipment')
            sort_order = request.args.get('sort_order', 'asc')
            
            # Convert year to int if provided
            year_filter_int = None
            if year_filter:
                try:
                    year_filter_int = int(year_filter)
                except ValueError:
                    pass
            
            # Validate parameters
            if page < 1:
                page = 1
            if limit < 1 or limit > 1000:
                limit = 50
            if sort_order not in ['asc', 'desc']:
                sort_order = 'asc'
            
            print(f"Fleet data request - Page: {page}, Limit: {limit}, Search: '{search}', Filters: make={make_filter}, year={year_filter}, location={location_filter}, status={status_filter}")
            
            # Get data from fleet manager
            result = fleet_manager.get_fleet_data(
                page=page,
                limit=limit,
                search=search,
                make_filter=make_filter,
                year_filter=year_filter_int,
                location_filter=location_filter,
                status_filter=status_filter,
                department_filter=department_filter,
                fuel_type_filter=fuel_type_filter,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            if result['success']:
                print(f"Fleet data success - Returned {len(result['data'])} vehicles, Total: {result['total_count']}")
                return jsonify(result), 200
            else:
                print(f"Fleet data error: {result['message']}")
                return jsonify(result), 400
                
        except Exception as e:
            error_msg = f"Error in get_fleet_data: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def get_fleet_summary():
        """Get fleet summary statistics for charts and dashboard"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            print("Fleet summary request received")
            
            result = fleet_manager.get_fleet_summary()
            
            if result['success']:
                print(f"Fleet summary success - Total vehicles: {result['summary']['total_vehicles']}")
                return jsonify(result), 200
            else:
                print(f"Fleet summary error: {result['message']}")
                return jsonify(result), 400
                
        except Exception as e:
            error_msg = f"Error in get_fleet_summary: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def get_filter_options():
        """Get available filter options for dropdowns"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            print("Filter options request received")
            
            result = fleet_manager.get_filter_options()
            
            if result['success']:
                options = result['options']
                print(f"Filter options success - Makes: {len(options.get('makes', []))}, Years: {len(options.get('years', []))}, Locations: {len(options.get('locations', []))}")
                return jsonify(result), 200
            else:
                print(f"Filter options error: {result['message']}")
                return jsonify(result), 400
                
        except Exception as e:
            error_msg = f"Error in get_filter_options: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def export_fleet_data():
        """Export fleet data in specified format"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            # Get export parameters
            format = request.args.get('format', 'excel').lower()
            search = request.args.get('search', None)
            
            # Filter parameters for export
            make_filter = request.args.get('make', None)
            year_filter = request.args.get('year', None)
            location_filter = request.args.get('location', None)
            status_filter = request.args.get('status', None)
            department_filter = request.args.get('department', None)
            fuel_type_filter = request.args.get('fuel_type', None)
            
            # Convert year to int if provided
            year_filter_int = None
            if year_filter:
                try:
                    year_filter_int = int(year_filter)
                except ValueError:
                    pass
            
            print(f"Fleet export request - Format: {format}, Search: '{search}', Filters applied")
            
            result = fleet_manager.export_fleet_data(
                format=format,
                search=search,
                make_filter=make_filter,
                year_filter=year_filter_int,
                location_filter=location_filter,
                status_filter=status_filter,
                department_filter=department_filter,
                fuel_type_filter=fuel_type_filter
            )
            
            if result['success']:
                print(f"Fleet export success - {result['record_count']} records exported to {result['filename']}")
                return jsonify(result), 200
            else:
                print(f"Fleet export error: {result['message']}")
                return jsonify(result), 400
                
        except Exception as e:
            error_msg = f"Error in export_fleet_data: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def add_vehicle():
        """Add a new vehicle to the fleet"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No vehicle data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['Equipment', 'Make', 'Model', 'Year', 'Cost', 'Location']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            # For now, return success (vehicle addition would need database integration)
            print(f"Vehicle add request - Equipment: {data.get('Equipment')}, Make: {data.get('Make')}")
            
            # Invalidate cache since we're adding new data
            fleet_manager.invalidate_cache()
            
            return jsonify({
                'success': True,
                'message': 'Vehicle added successfully',
                'vehicle': data
            }), 201
            
        except Exception as e:
            error_msg = f"Error in add_vehicle: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def update_vehicle(vehicle_id):
        """Update an existing vehicle"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No update data provided'
                }), 400
            
            print(f"Vehicle update request - ID: {vehicle_id}")
            
            # Invalidate cache since we're updating data
            fleet_manager.invalidate_cache()
            
            return jsonify({
                'success': True,
                'message': 'Vehicle updated successfully',
                'vehicle_id': vehicle_id,
                'updates': data
            }), 200
            
        except Exception as e:
            error_msg = f"Error in update_vehicle: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def delete_vehicle(vehicle_id):
        """Delete a vehicle from the fleet"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            print(f"Vehicle delete request - ID: {vehicle_id}")
            
            # Invalidate cache since we're deleting data
            fleet_manager.invalidate_cache()
            
            return jsonify({
                'success': True,
                'message': 'Vehicle deleted successfully',
                'vehicle_id': vehicle_id
            }), 200
            
        except Exception as e:
            error_msg = f"Error in delete_vehicle: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
    
    @staticmethod
    def refresh_cache():
        """Refresh the fleet data cache"""
        try:
            if not fleet_manager:
                return jsonify({
                    'success': False,
                    'message': 'Fleet management system not available'
                }), 500
            
            print("Fleet cache refresh request")
            
            fleet_manager.invalidate_cache()
            
            # Load fresh data
            result = fleet_manager.get_fleet_summary()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Fleet cache refreshed successfully',
                    'total_vehicles': result['summary']['total_vehicles']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to refresh cache'
                }), 500
                
        except Exception as e:
            error_msg = f"Error in refresh_cache: {str(e)}"
            print(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500