"""
Excel Data Controller
Handles HTTP requests for Excel file data operations
"""

from flask import request, jsonify
from services.excel_data_service import ExcelDataService
from typing import Dict, Any, Optional

class ExcelDataController:
    """Controller for Excel data operations"""
    
    @staticmethod
    def get_available_files():
        """Get list of available Excel files"""
        try:
            files = ExcelDataService.get_available_files()
            
            # Get detailed info for each file
            file_details = {}
            for file_key in files.keys():
                file_details[file_key] = ExcelDataService.get_file_info(file_key)
            
            return jsonify({
                'success': True,
                'available_files': files,
                'file_details': file_details
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_file_info(file_key: str):
        """Get detailed information about a specific Excel file"""
        try:
            info = ExcelDataService.get_file_info(file_key)
            
            if not info.get('file_exists', False):
                return jsonify({
                    'success': False,
                    'error': f"File '{file_key}' not found or cannot be read",
                    'file_info': info
                }), 404
            
            return jsonify({
                'success': True,
                'file_info': info
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'file_key': file_key
            }), 500
    
    @staticmethod
    def get_file_data(file_key: str):
        """Get paginated and filtered data from Excel file"""
        try:
            # Parse query parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 50))
            search_query = request.args.get('search', None)
            sort_column = request.args.get('sort_column', None)
            sort_direction = request.args.get('sort_direction', 'asc')
            sheet_name = request.args.get('sheet', None)
            
            # Parse column filters (format: column_name=value)
            column_filters = {}
            for key, value in request.args.items():
                if key.startswith('filter_'):
                    column_name = key.replace('filter_', '')
                    column_filters[column_name] = value
            
            # Parse value filters from JSON if provided
            value_filters = None
            if request.args.get('value_filters'):
                try:
                    import json
                    value_filters = json.loads(request.args.get('value_filters'))
                except:
                    pass
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 1000:
                page_size = 50
            
            # Get filtered data
            result = ExcelDataService.get_data_with_filters(
                file_key=file_key,
                page=page,
                page_size=page_size,
                search_query=search_query,
                column_filters=column_filters if column_filters else None,
                value_filters=value_filters,
                sort_column=sort_column,
                sort_direction=sort_direction,
                sheet_name=sheet_name
            )
            
            if not result['success']:
                return jsonify(result), 400
            
            return jsonify(result), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f"Invalid parameter: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'file_key': file_key
            }), 500
    
    @staticmethod
    def get_column_stats(file_key: str, column: str):
        """Get statistics for a specific column"""
        try:
            sheet_name = request.args.get('sheet', None)
            
            # Read the file
            df = ExcelDataService.read_excel_file(file_key, sheet_name)
            
            # Get column statistics
            stats = ExcelDataService.get_column_stats(df, column)
            
            if 'error' in stats:
                return jsonify({
                    'success': False,
                    'error': stats['error'],
                    'file_key': file_key,
                    'column': column
                }), 404
            
            return jsonify({
                'success': True,
                'column_stats': stats,
                'file_key': file_key
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'file_key': file_key,
                'column': column
            }), 500
    
    @staticmethod
    def search_across_files():
        """Search across all available Excel files"""
        try:
            search_query = request.args.get('search', '')
            max_results_per_file = int(request.args.get('max_results', 10))
            
            if not search_query:
                return jsonify({
                    'success': False,
                    'error': 'Search query is required'
                }), 400
            
            available_files = ExcelDataService.get_available_files()
            search_results = {}
            
            for file_key in available_files.keys():
                try:
                    result = ExcelDataService.get_data_with_filters(
                        file_key=file_key,
                        page=1,
                        page_size=max_results_per_file,
                        search_query=search_query
                    )
                    
                    if result['success'] and result['data']:
                        search_results[file_key] = {
                            'matches_found': len(result['data']),
                            'total_matches': result['pagination']['total_rows'],
                            'sample_data': result['data'],
                            'columns': result['columns']
                        }
                except:
                    # Skip files that can't be processed
                    continue
            
            return jsonify({
                'success': True,
                'search_query': search_query,
                'results': search_results,
                'files_searched': list(available_files.keys())
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def get_file_data_post(file_key: str):
        """Get file data using POST method for complex filters"""
        try:
            data = request.get_json() or {}
            
            # Extract parameters from POST body
            page = data.get('page', 1)
            page_size = data.get('page_size', 50)
            search_query = data.get('search')
            column_filters = data.get('column_filters')
            value_filters = data.get('value_filters')
            sort_column = data.get('sort_column')
            sort_direction = data.get('sort_direction', 'asc')
            sheet_name = data.get('sheet')
            
            # Validate parameters
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 1000:
                page_size = 50
            
            # Get filtered data
            result = ExcelDataService.get_data_with_filters(
                file_key=file_key,
                page=page,
                page_size=page_size,
                search_query=search_query,
                column_filters=column_filters,
                value_filters=value_filters,
                sort_column=sort_column,
                sort_direction=sort_direction,
                sheet_name=sheet_name
            )
            
            if not result['success']:
                return jsonify(result), 400
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'file_key': file_key
            }), 500