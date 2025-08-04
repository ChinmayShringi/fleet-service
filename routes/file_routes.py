"""
File Routes
API endpoints for file operations
"""

from flask import Blueprint
from controllers.file_controller import FileController

file_bp = Blueprint('files', __name__, url_prefix='/api/files')

# Vehicle fleet data endpoints
@file_bp.route('/vehicle-fleet/upload', methods=['POST'])
def upload_vehicle_fleet():
    """Upload vehicle fleet master data Excel file"""
    return FileController.upload_vehicle_fleet()

@file_bp.route('/vehicle-fleet/data', methods=['GET'])
def get_vehicle_fleet_data():
    """Get all vehicle fleet data"""
    return FileController.get_vehicle_fleet_data()

# Equipment lifecycle data endpoints  
@file_bp.route('/equipment-lifecycle/upload', methods=['POST'])
def upload_equipment_lifecycle():
    """Upload equipment lifecycle reference Excel file"""
    return FileController.upload_equipment_lifecycle()