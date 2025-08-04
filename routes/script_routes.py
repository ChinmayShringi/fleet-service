"""
Script Routes
API endpoints for running utility scripts
"""

from flask import Blueprint
from controllers.script_controller import ScriptController

script_bp = Blueprint('scripts', __name__, url_prefix='/api/scripts')

@script_bp.route('/excel-reader/run', methods=['POST'])
def run_excel_reader():
    """Run excel reader to generate pivot tables"""
    return ScriptController.run_excel_reader()

@script_bp.route('/lob-pivot-generator/run', methods=['POST'])
def run_lob_pivot_generator():
    """Run LOB pivot generator"""
    return ScriptController.run_lob_pivot_generator()

@script_bp.route('/ool-reader/run', methods=['POST'])
def run_ool_reader():
    """Run OOL reader to update data"""
    return ScriptController.run_ool_reader()