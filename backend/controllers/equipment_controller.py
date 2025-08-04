"""
Equipment Controller
Handles HTTP requests for equipment reallocation and replacement schedule updates
"""

from flask import jsonify, request
from services.equipment_service import EquipmentService

class EquipmentController:
    
    @staticmethod
    def update_replacement_schedule():
        """Update equipment replacement schedule"""
        try:
            # Validate request
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Request must be JSON'
                }), 400
            
            data = request.json
            equipment_ids = data.get('equipmentIds', [])
            new_replacement_year = data.get('newReplacementYear')
            
            # Validate required fields
            if not equipment_ids:
                return jsonify({
                    'success': False,
                    'message': 'equipmentIds is required and must be a non-empty list'
                }), 400
            
            if not isinstance(equipment_ids, list):
                return jsonify({
                    'success': False,
                    'message': 'equipmentIds must be a list'
                }), 400
            
            if new_replacement_year is None:
                return jsonify({
                    'success': False,
                    'message': 'newReplacementYear is required'
                }), 400
            
            if not isinstance(new_replacement_year, int):
                return jsonify({
                    'success': False,
                    'message': 'newReplacementYear must be an integer'
                }), 400
            
            # Call service
            result = EquipmentService.update_replacement_schedule(
                equipment_ids=equipment_ids,
                new_replacement_year=new_replacement_year
            )
            
            # Return appropriate HTTP status
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to update equipment replacement schedule: {str(e)}'
            }), 500
    
    @staticmethod
    def get_equipment_info():
        """Get information about specific equipment IDs"""
        try:
            # Get equipment IDs from query parameters or request body
            equipment_ids = []
            
            if request.is_json and request.json:
                equipment_ids = request.json.get('equipmentIds', [])
            else:
                # Try to get from query parameters
                ids_param = request.args.get('ids', '')
                if ids_param:
                    equipment_ids = [id.strip() for id in ids_param.split(',') if id.strip()]
            
            if not equipment_ids:
                return jsonify({
                    'success': False,
                    'message': 'equipmentIds is required (either in JSON body or as query parameter "ids")'
                }), 400
            
            # Call service
            result = EquipmentService.get_equipment_info(equipment_ids)
            
            # Return appropriate HTTP status
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to get equipment info: {str(e)}'
            }), 500