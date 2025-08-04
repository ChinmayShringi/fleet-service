"""
Script Controller
Handles HTTP requests for running utility scripts
"""

from flask import jsonify
from services.script_service import ScriptService

class ScriptController:
    
    @staticmethod
    def run_excel_reader():
        """Run excel reader to generate pivot tables"""
        try:
            result = ScriptService.run_excel_reader()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to run excel reader: {str(e)}'
            }), 500
    
    @staticmethod
    def run_lob_pivot_generator():
        """Run LOB pivot generator"""
        try:
            result = ScriptService.run_lob_pivot_generator()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to run LOB pivot generator: {str(e)}'
            }), 500
    
    @staticmethod
    def run_ool_reader():
        """Run OOL reader to update data"""
        try:
            result = ScriptService.run_ool_reader()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to run OOL reader: {str(e)}'
            }), 500