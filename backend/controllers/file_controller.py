"""
File Controller
Handles HTTP requests for file operations
"""

from flask import jsonify, request
from services.file_service import FileService
from constants.file_constants import VEHICLE_FLEET_DATA, EQUIPMENT_LIFECYCLE_DATA

class FileController:
    
    @staticmethod
    def upload_vehicle_fleet():
        """Upload vehicle fleet master data"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No file provided'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            if not file.filename.endswith('.xlsx'):
                return jsonify({
                    'success': False,
                    'message': 'Only .xlsx files are allowed'
                }), 400
            
            # Upload the file
            result = FileService.upload_file(file, 'vehicle_fleet_master_data.xlsx')
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Upload failed: {str(e)}'
            }), 500
    
    @staticmethod
    def get_vehicle_fleet_data():
        """Get all vehicle fleet data"""
        try:
            result = FileService.get_file_data(VEHICLE_FLEET_DATA)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to fetch data: {str(e)}'
            }), 500
    
    @staticmethod
    def upload_equipment_lifecycle():
        """Upload equipment lifecycle reference data"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No file provided'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            if not file.filename.endswith('.xlsx'):
                return jsonify({
                    'success': False,
                    'message': 'Only .xlsx files are allowed'
                }), 400
            
            # Upload the file
            result = FileService.upload_file(file, 'equipment_lifecycle_reference.xlsx')
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Upload failed: {str(e)}'
            }), 500