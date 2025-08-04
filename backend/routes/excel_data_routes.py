"""
Excel Data Routes
Routes for Excel file data operations
"""

from flask import Blueprint
from controllers.excel_data_controller import ExcelDataController

# Create blueprint
excel_data_bp = Blueprint('excel_data', __name__, url_prefix='/api/excel')

# Available files endpoint
@excel_data_bp.route('/files', methods=['GET'])
def get_available_files():
    """
    GET /api/excel/files
    Get list of available Excel files with basic information
    """
    return ExcelDataController.get_available_files()

# File information endpoint
@excel_data_bp.route('/files/<file_key>/info', methods=['GET'])
def get_file_info(file_key):
    """
    GET /api/excel/files/{file_key}/info
    Get detailed information about a specific Excel file
    """
    return ExcelDataController.get_file_info(file_key)

# File data endpoint (GET with query parameters)
@excel_data_bp.route('/files/<file_key>/data', methods=['GET'])
def get_file_data(file_key):
    """
    GET /api/excel/files/{file_key}/data
    Get paginated and filtered data from Excel file
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 1000)
    - search: Global search query
    - sort_column: Column to sort by
    - sort_direction: Sort direction (asc/desc, default: asc)
    - sheet: Excel sheet name (optional)
    - filter_{column_name}: Filter by column value
    - value_filters: JSON string with range filters
    
    Example:
    /api/excel/files/vehicle_fleet_master_data/data?page=1&page_size=25&search=Ford&filter_Make=Ford&sort_column=Year&sort_direction=desc
    """
    return ExcelDataController.get_file_data(file_key)

# File data endpoint (POST for complex filters)
@excel_data_bp.route('/files/<file_key>/data', methods=['POST'])
def get_file_data_post(file_key):
    """
    POST /api/excel/files/{file_key}/data
    Get paginated and filtered data using POST for complex filters
    
    Request Body:
    {
        "page": 1,
        "page_size": 50,
        "search": "search query",
        "column_filters": {
            "Make": "Ford",
            "Year": [2020, 2021, 2022]
        },
        "value_filters": {
            "Cost": {"min": 20000, "max": 50000},
            "Year": {"min": 2018}
        },
        "sort_column": "Cost",
        "sort_direction": "desc",
        "sheet": "Sheet1"
    }
    """
    return ExcelDataController.get_file_data_post(file_key)

# Column statistics endpoint
@excel_data_bp.route('/files/<file_key>/columns/<column>/stats', methods=['GET'])
def get_column_stats(file_key, column):
    """
    GET /api/excel/files/{file_key}/columns/{column}/stats
    Get statistics for a specific column in the Excel file
    
    Query Parameters:
    - sheet: Excel sheet name (optional)
    """
    return ExcelDataController.get_column_stats(file_key, column)

# Global search endpoint
@excel_data_bp.route('/search', methods=['GET'])
def search_across_files():
    """
    GET /api/excel/search
    Search across all available Excel files
    
    Query Parameters:
    - search: Search query (required)
    - max_results: Maximum results per file (default: 10)
    """
    return ExcelDataController.search_across_files()

# Specific file shortcuts for commonly used files

# Vehicle Fleet Master Data
@excel_data_bp.route('/vehicle-fleet/data', methods=['GET', 'POST'])
def get_vehicle_fleet_data():
    """Shortcut for vehicle fleet master data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('vehicle_fleet_master_data')
    else:
        return ExcelDataController.get_file_data_post('vehicle_fleet_master_data')

@excel_data_bp.route('/vehicle-fleet/info', methods=['GET'])
def get_vehicle_fleet_info():
    """Shortcut for vehicle fleet info"""
    return ExcelDataController.get_file_info('vehicle_fleet_master_data')

# Equipment Lifecycle Reference
@excel_data_bp.route('/equipment-lifecycle/data', methods=['GET', 'POST'])
def get_equipment_lifecycle_data():
    """Shortcut for equipment lifecycle reference data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('equipment_lifecycle_reference')
    else:
        return ExcelDataController.get_file_data_post('equipment_lifecycle_reference')

@excel_data_bp.route('/equipment-lifecycle/info', methods=['GET'])
def get_equipment_lifecycle_info():
    """Shortcut for equipment lifecycle info"""
    return ExcelDataController.get_file_info('equipment_lifecycle_reference')

# Electric Vehicle Budget Analysis
@excel_data_bp.route('/electric-vehicle-budget/data', methods=['GET', 'POST'])
def get_electric_vehicle_budget_data():
    """Shortcut for electric vehicle budget analysis data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('electric_vehicle_budget_analysis')
    else:
        return ExcelDataController.get_file_data_post('electric_vehicle_budget_analysis')

@excel_data_bp.route('/electric-vehicle-budget/info', methods=['GET'])
def get_electric_vehicle_budget_info():
    """Shortcut for electric vehicle budget info"""
    return ExcelDataController.get_file_info('electric_vehicle_budget_analysis')

# Radio Equipment Cost Analysis
@excel_data_bp.route('/radio-equipment-cost/data', methods=['GET', 'POST'])
def get_radio_equipment_cost_data():
    """Shortcut for radio equipment cost analysis data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('radio_equipment_cost_analysis')
    else:
        return ExcelDataController.get_file_data_post('radio_equipment_cost_analysis')

@excel_data_bp.route('/radio-equipment-cost/info', methods=['GET'])  
def get_radio_equipment_cost_info():
    """Shortcut for radio equipment cost info"""
    return ExcelDataController.get_file_info('radio_equipment_cost_analysis')

# Vehicle Replacement Detailed Forecast
@excel_data_bp.route('/vehicle-replacement-forecast/data', methods=['GET', 'POST'])
def get_vehicle_replacement_forecast_data():
    """Shortcut for vehicle replacement detailed forecast data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('vehicle_replacement_detailed_forecast')
    else:
        return ExcelDataController.get_file_data_post('vehicle_replacement_detailed_forecast')

@excel_data_bp.route('/vehicle-replacement-forecast/info', methods=['GET'])
def get_vehicle_replacement_forecast_info():
    """Shortcut for vehicle replacement forecast info"""
    return ExcelDataController.get_file_info('vehicle_replacement_detailed_forecast')

# Vehicle Replacement By Category
@excel_data_bp.route('/vehicle-replacement-category/data', methods=['GET', 'POST'])
def get_vehicle_replacement_category_data():
    """Shortcut for vehicle replacement by category data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('vehicle_replacement_by_category')
    else:
        return ExcelDataController.get_file_data_post('vehicle_replacement_by_category')

@excel_data_bp.route('/vehicle-replacement-category/info', methods=['GET'])
def get_vehicle_replacement_category_info():
    """Shortcut for vehicle replacement by category info"""
    return ExcelDataController.get_file_info('vehicle_replacement_by_category')

# Equipment Lifecycle By Business Unit
@excel_data_bp.route('/equipment-lifecycle-business/data', methods=['GET', 'POST'])
def get_equipment_lifecycle_business_data():
    """Shortcut for equipment lifecycle by business unit data"""
    if request.method == 'GET':
        return ExcelDataController.get_file_data('equipment_lifecycle_by_business_unit')
    else:
        return ExcelDataController.get_file_data_post('equipment_lifecycle_by_business_unit')

@excel_data_bp.route('/equipment-lifecycle-business/info', methods=['GET'])
def get_equipment_lifecycle_business_info():
    """Shortcut for equipment lifecycle by business unit info"""
    return ExcelDataController.get_file_info('equipment_lifecycle_by_business_unit')

# Import request for the shortcuts
from flask import request