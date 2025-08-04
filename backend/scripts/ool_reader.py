import pandas as pd
import os
from constants.file_constants import get_input_file, get_output_file, get_input_file_safe, ensure_database_directory

def read_ool_headers():
    """Read OOL.xlsx file and print its headers with multi-level structure"""
    try:
        # Check if file exists
        ool_file = get_input_file_safe("EQUIPMENT_LIFECYCLE_REFERENCE")
        if ool_file is None:
            return
        
        # Read the Excel file with multi-level headers
        print(f"Reading {ool_file} file...")
        
        # First, read with default settings to see structure
        df_default = pd.read_excel(ool_file)
        
        # Try reading with multi-level headers (first 2 rows as headers)
        df_multiheader = pd.read_excel(ool_file, header=[0, 1])
        
        print("\n=== OOL.xlsx Structure Analysis ===")
        print(f"Total columns: {len(df_default.columns)}")
        print(f"Total rows: {len(df_default)}")
        
        print("\n=== Default Headers ===")
        for i, header in enumerate(df_default.columns, 1):
            print(f"{i:2d}. {header}")
        
        print("\n=== Multi-Level Headers Structure ===")
        print("Based on your description, the structure should be:")
        print("\nSection 1: Vehicle Lifecycle")
        print("  - ObjectType")
        print("  - Equipment descriptn") 
        print("  - Life Cycle")
        
        print("\nSection 2: Vehicle Depreciation")
        print("  - ObjectType")
        print("  - Equipment descriptn")
        print("  - Dep. Years")
        
        print("\nSection 3: Vehicle Weight Category - Heavy / Light / Power")
        print("  - L.H.P")
        print("  - ObjectType") 
        print("  - Equipment descriptn")
        
        # Try to read with multi-level headers and show the result
        try:
            print(f"\n=== Multi-Level Headers (if available) ===")
            for i, header in enumerate(df_multiheader.columns, 1):
                print(f"{i:2d}. {header}")
        except:
            print("Multi-level header reading not successful - file may have different structure")
        
        # Show first few rows to understand the data better
        print(f"\n=== First 3 Data Rows ===")
        print(df_default.head(3).to_string())
        
        print("\n=== Column Data Types ===")
        for header, dtype in df_default.dtypes.items():
            print(f"{header}: {dtype}")
            
    except Exception as e:
        print(f"Error reading OOL.xlsx: {str(e)}")

def read_ool_data_properly():
    """Read OOL.xlsx file with proper header structure"""
    try:
        # Read the file skipping the first 2 rows and no header
        ool_file = get_input_file_safe("EQUIPMENT_LIFECYCLE_REFERENCE")
        if ool_file is None:
            print("No equipment lifecycle reference data found. Please ensure the file exists.")
            return None
        df = pd.read_excel(ool_file, skiprows=2, header=None)
        
        # Set proper column names based on the structure you described
        column_names = [
            # Vehicle Lifecycle section (3 columns)
            'VL_ObjectType', 'VL_Equipment_Description', 'VL_Life_Cycle',
            # Empty columns (placeholders)
            'Empty_1', 'Empty_2', 
            # Vehicle Depreciation section (3 columns) 
            'VD_ObjectType', 'VD_Equipment_Description', 'VD_Dep_Years',
            # Empty columns (placeholders)
            'Empty_3', 'Empty_4',
            # Vehicle Weight Category section (3 columns)
            'VWC_LHP', 'VWC_ObjectType', 'VWC_Equipment_Description'
        ]
        
        df.columns = column_names
        
        print("\n=== Properly Structured OOL Data ===")
        print(f"Total columns: {len(df.columns)}")
        print(f"Total rows: {len(df)}")
        
        print("\n=== Column Names Applied ===")
        for i, header in enumerate(df.columns, 1):
            print(f"{i:2d}. {header}")
        
        # Group columns by sections
        print("\n=== Grouped by Sections ===")
        
        print("\n1. Vehicle Lifecycle Section:")
        lifecycle_cols = ['VL_ObjectType', 'VL_Equipment_Description', 'VL_Life_Cycle']
        for i, col in enumerate(lifecycle_cols, 1):
            print(f"   {i}. {col}")
        
        print("\n2. Vehicle Depreciation Section:")
        depreciation_cols = ['VD_ObjectType', 'VD_Equipment_Description', 'VD_Dep_Years']
        for i, col in enumerate(depreciation_cols, 1):
            print(f"   {i}. {col}")
        
        print("\n3. Vehicle Weight Category Section:")
        weight_cols = ['VWC_LHP', 'VWC_ObjectType', 'VWC_Equipment_Description']
        for i, col in enumerate(weight_cols, 1):
            print(f"   {i}. {col}")
        
        # Remove the first row which contains the original headers
        df_clean = df.iloc[1:].copy()
        
        # Show first few rows of actual data
        print(f"\n=== First 5 Data Rows (after removing header row) ===")
        print(df_clean.head(5).to_string())
        
        # Show some statistics
        print(f"\n=== Data Summary ===")
        print(f"Cleaned data rows: {len(df_clean)}")
        
        # Show unique values in key columns
        print(f"\nUnique ObjectTypes in Vehicle Lifecycle: {df_clean['VL_ObjectType'].dropna().nunique()}")
        print(f"Unique L.H.P values: {df_clean['VWC_LHP'].dropna().nunique()}")
        
        return df_clean
        
    except Exception as e:
        print(f"Error reading OOL.xlsx properly: {str(e)}")
        return None

def update_equipment_replacement_schedule(equipment_ids, new_replacement_year):
    """
    Update equipment replacement schedule based on lifecycle data
    
    Args:
        equipment_ids (list): List of equipment IDs to update (e.g., ['VV12205', 'VV18683'])
        new_replacement_year (int): New replacement year (e.g., 2027)
    """
    try:
        # Read vehicle fleet master data
        print("Reading vehicle fleet master data...")
        data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
        if data_file is None:
            print("ERROR: Vehicle fleet master data file not found")
            return None
        df_data = pd.read_excel(data_file)
        
        # Read OOL.xlsx with proper structure
        print("Reading equipment lifecycle reference...")
        ool_file = get_input_file_safe("EQUIPMENT_LIFECYCLE_REFERENCE")
        if ool_file is None:
            print("ERROR: Equipment lifecycle reference file not found")
            return None
        df_ool = pd.read_excel(ool_file, skiprows=2, header=None)
        
        # Set proper column names for OOL data
        ool_column_names = [
            'VL_ObjectType', 'VL_Equipment_Description', 'VL_Life_Cycle',
            'Empty_1', 'Empty_2', 
            'VD_ObjectType', 'VD_Equipment_Description', 'VD_Dep_Years',
            'Empty_3', 'Empty_4',
            'VWC_LHP', 'VWC_ObjectType', 'VWC_Equipment_Description'
        ]
        df_ool.columns = ool_column_names
        
        # Remove header row and clean data
        df_ool = df_ool.iloc[1:].copy()
        
        print(f"\n=== Processing {len(equipment_ids)} equipment IDs ===")
        
        # Years range for forecast (2026-2035)
        years = range(2026, 2036)
        
        for equipment_id in equipment_ids:
            print(f"\nProcessing Equipment ID: {equipment_id}")
            
            # Find equipment in data.xlsx
            equipment_row = df_data[df_data['Equipment'] == equipment_id]
            
            if equipment_row.empty:
                print(f"  ERROR: Equipment {equipment_id} not found in data.xlsx")
                continue
                
            # Get ObjectType and Equipment description
            object_type = equipment_row['ObjectType'].iloc[0]
            equipment_desc = equipment_row['Equipment descriptn'].iloc[0]
            
            print(f"  ObjectType: {object_type}")
            print(f"  Equipment Description: {equipment_desc}")
            
            # Find matching row in OOL.xlsx (Vehicle Lifecycle section)
            # Match only on Equipment description for now
            ool_match = df_ool[df_ool['VL_Equipment_Description'] == equipment_desc]
            
            if ool_match.empty:
                print(f"  ERROR: No matching lifecycle data found in OOL.xlsx")
                continue
                
            # Get Life Cycle value
            life_cycle = ool_match['VL_Life_Cycle'].iloc[0]
            
            if pd.isna(life_cycle) or not isinstance(life_cycle, (int, float)):
                print(f"  ERROR: Invalid Life Cycle value: {life_cycle}")
                continue
                
            life_cycle = int(life_cycle)
            print(f"  Life Cycle: {life_cycle} years")
            
            # Calculate replacement years based on life cycle
            replacement_years = []
            current_year = new_replacement_year
            while current_year <= 2035:
                replacement_years.append(current_year)
                current_year += life_cycle
                
            print(f"  Replacement schedule: {replacement_years}")
            
            # Update forecast counts - first set all years to 0
            equipment_index = equipment_row.index[0]
            for year in years:
                forecast_col = f'{year} Forecast Count'
                if forecast_col in df_data.columns:
                    df_data.loc[equipment_index, forecast_col] = 0
            
            # Set replacement years to 1
            for year in replacement_years:
                forecast_col = f'{year} Forecast Count'
                if forecast_col in df_data.columns:
                    df_data.loc[equipment_index, forecast_col] = 1
                    print(f"    SUCCESS: Set {year} Forecast Count = 1")
                else:
                    print(f"    WARNING: Column {forecast_col} not found")
        
        # Save updated data back to Excel
        output_file = get_input_file("VEHICLE_FLEET_MASTER_DATA")
        df_data.to_excel(output_file, index=False)
        print(f"\nSUCCESS: Updated data saved to {output_file}")
        
        return df_data
        
    except Exception as e:
        print(f"ERROR: Equipment replacement schedule update failed: {str(e)}")
        return None

def update_specific_equipment(equipment_ids, new_replacement_year):
    """
    Simple wrapper function to update specific equipment replacement schedules
    
    Args:
        equipment_ids (list or str): Equipment ID(s) to update
        new_replacement_year (int): New replacement year
    
    Example usage:
        # Single equipment
        update_specific_equipment('VV12205', 2027)
        
        # Multiple equipment
        update_specific_equipment(['VV12205', 'VV18683', 'VV18686'], 2027)
    """
    # Convert single string to list
    if isinstance(equipment_ids, str):
        equipment_ids = [equipment_ids]
    
    print(f"=== Equipment Replacement Schedule Update ===")
    print(f"Equipment IDs: {equipment_ids}")
    print(f"New replacement year: {new_replacement_year}")
    
    return update_equipment_replacement_schedule(equipment_ids, new_replacement_year)

def demo_equipment_update():
    """Demo function showing the equipment update process"""
    print("=== DEMO: Equipment Replacement Schedule Update ===")
    
    # Example: Update VV12205 to be replaced in 2027
    equipment_ids = ['VV12205']
    new_replacement_year = 2027
    
    print(f"Example: Moving equipment {equipment_ids} to replacement year {new_replacement_year}")
    update_equipment_replacement_schedule(equipment_ids, new_replacement_year)

def save_pivot_to_excel(pivot_data, lifecycle_stats, not_found_count, total_equipment_count):
    """
    Save the LOB pivot table to an Excel file
    """
    try:
        output_filename = get_output_file("EQUIPMENT_LIFECYCLE_BY_BUSINESS_UNIT")
        
        # Create a list to store all data for Excel
        excel_data = []
        
        # Add summary header
        excel_data.append(['LOB Equipment Lifecycle Pivot Table'])
        excel_data.append(['Total Equipment:', total_equipment_count])
        excel_data.append([''])  # Empty row
        
        # Add data for each LOB
        for lob, equipment_list in pivot_data.items():
            excel_data.append([lob])
            excel_data.append(['Summary Total:', len(equipment_list), 'equipment items'])
            
            # Sort equipment by ID for better readability
            sorted_equipment = sorted(equipment_list, key=lambda x: x['equipment_id'])
            
            for item in sorted_equipment:
                life_cycle_display = f"{item['life_cycle']} years" if isinstance(item['life_cycle'], int) else item['life_cycle']
                excel_data.append([
                    item['equipment_id'], 
                    item['object_type'], 
                    life_cycle_display,
                    item['equipment_desc']
                ])
            
            excel_data.append([''])  # Empty row between LOBs
        
        # Add summary statistics
        excel_data.append(['=== SUMMARY STATISTICS ==='])
        excel_data.append(['Life Cycle Distribution:'])
        
        for cycle, count in sorted(lifecycle_stats.items()):
            excel_data.append([f"{cycle} years:", count, 'equipment items'])
        
        if not_found_count > 0:
            excel_data.append(['No lifecycle data:', not_found_count, 'equipment items'])
        
        # Create DataFrame and save to Excel
        df_export = pd.DataFrame(excel_data)
        df_export.to_excel(output_filename, index=False, header=False)
        
        print(f"\nSUCCESS: Pivot table saved to {output_filename}")
        
    except Exception as e:
        print(f"WARNING: Could not save pivot table to Excel: {str(e)}")

def create_lob_lifecycle_pivot():
    """
    Create a pivot table showing equipment grouped by LOB with lifecycle information
    """
    try:
        print("=== LOB Equipment Lifecycle Pivot Table ===")
        
        # Read data.xlsx
        data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
        if data_file is None:
            print("No vehicle fleet master data found. Please ensure the file exists.")
            return None
        print(f"Reading {data_file}...")
        df_data = pd.read_excel(data_file)
        
        # Read OOL.xlsx with proper structure
        ool_file = get_input_file_safe("EQUIPMENT_LIFECYCLE_REFERENCE")
        if ool_file is None:
            print("No equipment lifecycle reference data found. Please ensure the file exists.")
            return None
        print(f"Reading {ool_file}...")
        df_ool = pd.read_excel(ool_file, skiprows=2, header=None)
        
        # Set proper column names for OOL data
        ool_column_names = [
            'VL_ObjectType', 'VL_Equipment_Description', 'VL_Life_Cycle',
            'Empty_1', 'Empty_2', 
            'VD_ObjectType', 'VD_Equipment_Description', 'VD_Dep_Years',
            'Empty_3', 'Empty_4',
            'VWC_LHP', 'VWC_ObjectType', 'VWC_Equipment_Description'
        ]
        df_ool.columns = ool_column_names
        df_ool = df_ool.iloc[1:].copy()  # Remove header row
        
        # Check if required columns exist
        required_columns = ['LOB from Location', 'Equipment', 'ObjectType', 'Equipment descriptn']
        missing_columns = [col for col in required_columns if col not in df_data.columns]
        
        if missing_columns:
            print(f"ERROR: Missing columns in data.xlsx: {missing_columns}")
            print("Available columns:", list(df_data.columns))
            return None
        
        # Get unique LOBs
        unique_lobs = df_data['LOB from Location'].dropna().unique()
        print(f"Found {len(unique_lobs)} unique LOBs")
        
        # Create pivot data structure
        pivot_data = {}
        total_equipment_count = 0
        
        for lob in sorted(unique_lobs):
            # Get all equipment for this LOB
            lob_equipment = df_data[df_data['LOB from Location'] == lob]
            
            equipment_details = []
            
            for _, row in lob_equipment.iterrows():
                equipment_id = row['Equipment']
                object_type = row['ObjectType']
                equipment_desc = row['Equipment descriptn']
                
                # Find lifecycle data in OOL.xlsx (match by Equipment description)
                ool_match = df_ool[df_ool['VL_Equipment_Description'] == equipment_desc]
                
                if not ool_match.empty:
                    life_cycle = ool_match['VL_Life_Cycle'].iloc[0]
                    try:
                        life_cycle = int(float(life_cycle)) if pd.notna(life_cycle) else "N/A"
                    except:
                        life_cycle = "N/A"
                else:
                    life_cycle = "Not Found"
                
                equipment_details.append({
                    'equipment_id': equipment_id,
                    'object_type': object_type,
                    'equipment_desc': equipment_desc,
                    'life_cycle': life_cycle
                })
                
                total_equipment_count += 1
            
            pivot_data[lob] = equipment_details
        
        # Display the pivot table
        print(f"\n=== PIVOT TABLE: Equipment by LOB ===")
        print(f"Total Equipment: {total_equipment_count}")
        print("=" * 60)
        
        for lob, equipment_list in pivot_data.items():
            print(f"\n{lob}")
            print(f" Summary Total: {len(equipment_list)} equipment items")
            
            # Sort equipment by ID for better readability
            sorted_equipment = sorted(equipment_list, key=lambda x: x['equipment_id'])
            
            for item in sorted_equipment:
                life_cycle_display = f"{item['life_cycle']} years" if isinstance(item['life_cycle'], int) else item['life_cycle']
                print(f" {item['equipment_id']} <{item['object_type']}> <{life_cycle_display}>")
        
        # Create summary statistics
        print(f"\n=== SUMMARY STATISTICS ===")
        lifecycle_stats = {}
        not_found_count = 0
        
        for equipment_list in pivot_data.values():
            for item in equipment_list:
                life_cycle = item['life_cycle']
                if isinstance(life_cycle, int):
                    lifecycle_stats[life_cycle] = lifecycle_stats.get(life_cycle, 0) + 1
                else:
                    not_found_count += 1
        
        print("Life Cycle Distribution:")
        for cycle, count in sorted(lifecycle_stats.items()):
            print(f"  {cycle} years: {count} equipment items")
        
        if not_found_count > 0:
            print(f"  No lifecycle data: {not_found_count} equipment items")
        
        # Save pivot table to Excel file
        save_pivot_to_excel(pivot_data, lifecycle_stats, not_found_count, total_equipment_count)
        
        return pivot_data
        
    except Exception as e:
        print(f"ERROR: Failed to create LOB lifecycle pivot: {str(e)}")
        return None

if __name__ == "__main__":
    read_ool_headers()
    print("\n" + "="*50)
    read_ool_data_properly()
    print("\n" + "="*50)
    demo_equipment_update()
    print("\n" + "="*50)
    create_lob_lifecycle_pivot()