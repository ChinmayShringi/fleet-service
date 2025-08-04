"""
Equipment Routes
API endpoints for equipment reallocation and replacement schedule management
"""

from flask import Blueprint
from controllers.equipment_controller import EquipmentController

equipment_bp = Blueprint('equipment', __name__, url_prefix='/api/equipment')

@equipment_bp.route('/reallocate', methods=['POST'])
def update_replacement_schedule():
    """Update equipment replacement schedule"""
    return EquipmentController.update_replacement_schedule()

@equipment_bp.route('/info', methods=['GET', 'POST'])
def get_equipment_info():
    """Get information about specific equipment IDs"""
    return EquipmentController.get_equipment_info()