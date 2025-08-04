"""
Health Routes
API endpoints for health checks
"""

from flask import Blueprint, jsonify
import os
from constants.file_constants import DATABASE_DIR

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'database': os.path.exists(DATABASE_DIR)
    })

@health_bp.route('/')
def index():
    """API information"""
    return jsonify({
        'service': 'Vehicle Fleet Management API',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'upload_vehicle_fleet': 'POST /api/files/vehicle-fleet/upload',
            'get_vehicle_fleet': 'GET /api/files/vehicle-fleet/data',
            'upload_equipment_lifecycle': 'POST /api/files/equipment-lifecycle/upload',
            'run_excel_reader': 'POST /api/scripts/excel-reader/run',
            'run_lob_pivot_generator': 'POST /api/scripts/lob-pivot-generator/run',
            'run_ool_reader': 'POST /api/scripts/ool-reader/run'
        }
    })