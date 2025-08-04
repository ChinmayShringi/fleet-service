"""
Vehicle Fleet Management API
Main Flask application with proper MVC structure
"""

from flask import Flask
from flask_cors import CORS
from constants.file_constants import (
    SERVER_HOST, 
    SERVER_PORT, 
    DEBUG_MODE,
    ensure_database_directory
)

# Import route blueprints
from routes.health_routes import health_bp
from routes.file_routes import file_bp
from routes.script_routes import script_bp
from routes.auth_routes import auth_bp

# Import services
from services.user_service import UserService

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file upload
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(script_bp)
    app.register_blueprint(auth_bp)
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("VEHICLE FLEET MANAGEMENT API")
    print("=" * 50)
    print(f"Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print("Available APIs:")
    print("  POST /api/files/vehicle-fleet/upload")
    print("  GET  /api/files/vehicle-fleet/data") 
    print("  POST /api/files/equipment-lifecycle/upload")
    print("  POST /api/scripts/excel-reader/run")
    print("  POST /api/scripts/lob-pivot-generator/run")
    print("  POST /api/scripts/ool-reader/run")
    print("  POST /api/auth/register")
    print("  POST /api/auth/login")
    print("  GET  /api/auth/users")
    print("  GET  /api/auth/stats")
    print("  GET  /health")
    print("=" * 50)
    print("DEFAULT ADMIN CREDENTIALS:")
    print("  Email: admin@gmail.com")
    print("  Password: admin")
    print("=" * 50)
    
    # Ensure database directory exists
    ensure_database_directory()
    
    # Create default admin user
    print("Creating default admin user...")
    UserService.create_default_admin()
    
    # Start server
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)