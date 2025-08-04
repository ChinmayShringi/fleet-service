"""
Simple Constants for Backend Service
"""

import os

# Server Configuration
SERVER_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
SERVER_PORT = int(os.getenv('FLASK_PORT', 3300))
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# API Configuration
API_TITLE = "Vehicle Fleet Management API"
API_VERSION = "1.0.0"

# Database
DATABASE_DIR = "database"

# Scripts
SCRIPTS_DIR = "scripts"

# Script paths
EXCEL_READER_SCRIPT = os.path.join(SCRIPTS_DIR, "excel_reader.py")
LOB_PIVOT_GENERATOR_SCRIPT = os.path.join(SCRIPTS_DIR, "lob_pivot_generator.py")
OOL_READER_SCRIPT = os.path.join(SCRIPTS_DIR, "ool_reader.py")
EQUIPMENT_UPDATER_SCRIPT = os.path.join(SCRIPTS_DIR, "equipment_updater.py")

# File paths  
VEHICLE_FLEET_DATA = os.path.join(DATABASE_DIR, "vehicle_fleet_master_data.xlsx")
EQUIPMENT_LIFECYCLE_DATA = os.path.join(DATABASE_DIR, "equipment_lifecycle_reference.xlsx")

# Input Files (for compatibility with existing scripts)
INPUT_FILES = {
    "VEHICLE_FLEET_MASTER_DATA": VEHICLE_FLEET_DATA,
    "EQUIPMENT_LIFECYCLE_REFERENCE": EQUIPMENT_LIFECYCLE_DATA
}

# Output Files
OUTPUT_FILES = {
    "VEHICLE_FLEET_UPDATED_DATA": os.path.join(DATABASE_DIR, "vehicle_fleet_updated_data.xlsx"),
    "EQUIPMENT_LIFECYCLE_BY_BUSINESS_UNIT": os.path.join(DATABASE_DIR, "equipment_lifecycle_by_business_unit.xlsx"),
    "ELECTRIC_VEHICLE_BUDGET_ANALYSIS": os.path.join(DATABASE_DIR, "electric_vehicle_budget_analysis.xlsx"),
    "RADIO_EQUIPMENT_COST_ANALYSIS": os.path.join(DATABASE_DIR, "radio_equipment_cost_analysis.xlsx"),
    "VEHICLE_REPLACEMENT_DETAILED_FORECAST": os.path.join(DATABASE_DIR, "vehicle_replacement_detailed_forecast.xlsx"),
    "VEHICLE_REPLACEMENT_BY_CATEGORY": os.path.join(DATABASE_DIR, "vehicle_replacement_by_category.xlsx"),
    "HEAVY_VEHICLE_EV_TRANSITION_ANALYSIS": os.path.join(DATABASE_DIR, "heavy_vehicle_ev_transition_analysis.xlsx"),
    "LIGHT_VAN_EV_TRANSITION_ANALYSIS": os.path.join(DATABASE_DIR, "light_van_ev_transition_analysis.xlsx")
}

# Sheet Names
SHEET_NAMES = {
    "EV_SUMMARY": "EV_Summary",
    "FREIGHTLINER_ANALYSIS": "Freightliner_Analysis",
    "VAN_ANALYSIS": "Van_Analysis",
    "VEHICLE_COUNTS": "Vehicle_Counts",
    "REPLACEMENT_COSTS": "Replacement_Costs",
    "COMBINED_SUMMARY": "Combined_Summary",
    "RADIO_COUNTS": "Radio_Counts",
    "RADIO_SPENDS": "Radio_Spends",
    "RAW_DATA": "Raw_Data",
    "DETAILED_HIERARCHICAL_SUMMARY": "Detailed_Hierarchical_Summary",
    "LHP_OBJECTTYPE_SUMMARY": "LHP_ObjectType_Summary"
}

def ensure_database_directory():
    """Create database directory if it doesn't exist"""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR, exist_ok=True)

def get_input_file(file_key):
    """Get input file path by key"""
    return INPUT_FILES[file_key]

def get_input_file_safe(file_key):
    """Get input file path with existence check"""
    file_path = get_input_file(file_key)
    if not os.path.exists(file_path):
        print(f"Warning: No data found: {file_path} does not exist")
        return None
    return file_path

def get_output_file(file_key):
    """Get output file path by key"""
    ensure_database_directory()
    return OUTPUT_FILES[file_key]

def get_sheet_name(sheet_key):
    """Get sheet name by key"""
    return SHEET_NAMES[sheet_key]