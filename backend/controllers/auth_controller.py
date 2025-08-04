"""
Authentication Controller
Handles HTTP requests for user authentication
"""

from flask import jsonify, request
from services.user_service import UserService

class AuthController:
    
    @staticmethod
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'message': f'{field} is required'
                    }), 400
            
            # Basic validation
            username = data['username'].strip()
            email = data['email'].strip()
            password = data['password']
            full_name = data.get('full_name', '').strip()
            role = data.get('role', 'user')
            
            if len(username) < 3:
                return jsonify({
                    'success': False,
                    'message': 'Username must be at least 3 characters'
                }), 400
            
            if len(password) < 6:
                return jsonify({
                    'success': False,
                    'message': 'Password must be at least 6 characters'
                }), 400
            
            if '@' not in email:
                return jsonify({
                    'success': False,
                    'message': 'Please provide a valid email'
                }), 400
            
            # Register user
            result = UserService.register_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name if full_name else None,
                role=role
            )
            
            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }), 500
    
    @staticmethod
    def login():
        """Login user"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400
            
            # Validate required fields
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400
            
            # Login user
            result = UserService.login_user(username.strip(), password)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Login failed: {str(e)}'
            }), 500
    
    @staticmethod
    def get_users():
        """Get all users (admin only)"""
        try:
            result = UserService.get_all_users()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to get users: {str(e)}'
            }), 500
    
    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        try:
            result = UserService.get_user_stats()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to get user stats: {str(e)}'
            }), 500