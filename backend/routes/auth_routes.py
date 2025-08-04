"""
Authentication Routes
API endpoints for user authentication and management
"""

from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    return AuthController.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    return AuthController.login()

@auth_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    return AuthController.get_users()

@auth_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    return AuthController.get_user_stats()