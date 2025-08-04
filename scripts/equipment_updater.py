"""
Equipment Replacement Schedule Updater

This script demonstrates how to update equipment replacement schedules
based on lifecycle data from OOL.xlsx.
"""

from ool_reader import update_specific_equipment
from constants.file_constants import get_input_file_safe

def debug_equipment_lookup(equipment_id):
    """Debug function to check what's happening with equipment lookup"""
    import pandas as pd
    
    print(f"=== DEBUGGING EQUIPMENT {equipment_id} ===")
    
    # Read data.xlsx
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Please ensure the file exists.")
        return
    print(f"1. Reading {data_file}...")
    df_data = pd.read_excel(data_file)
    
    # Find equipment in data.xlsx
    equipment_row = df_data[df_data['Equipment'] == equipment_id]
    
    if equipment_row.empty:
        print(f"  ERROR: Equipment {equipment_id} not found in data.xlsx")
        return
    
    # Get ObjectType and Equipment description
    object_type = equipment_row['ObjectType'].iloc[0]
    equipment_desc = equipment_row['Equipment descriptn'].iloc[0]
    
    print(f"  Found in data.xlsx:")
    print(f"    ObjectType: '{object_type}'")
    print(f"    Equipment descriptn: '{equipment_desc}'")
    
    # Read OOL.xlsx
    ool_file = get_input_file_safe("EQUIPMENT_LIFECYCLE_REFERENCE")
    if ool_file is None:
        print("No equipment lifecycle reference data found. Please ensure the file exists.")
        return
    print(f"\n2. Reading {ool_file}...")
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
    
    print(f"  OOL data shape: {df_ool.shape}")
    
    # Check all ObjectTypes in OOL
    unique_object_types = df_ool['VL_ObjectType'].dropna().unique()
    print(f"\n3. Available ObjectTypes in OOL.xlsx:")
    for i, ot in enumerate(unique_object_types, 1):
        print(f"    {i:2d}. '{ot}'")
    
    # Check if our ObjectType exists (case insensitive)
    matching_object_types = [ot for ot in unique_object_types if str(ot).upper() == str(object_type).upper()]
    print(f"\n4. ObjectType matching check:")
    print(f"  Looking for: '{object_type}'")
    print(f"  Case-insensitive matches: {matching_object_types}")
    
    # Check all rows with the matching ObjectType
    if matching_object_types:
        actual_object_type = matching_object_types[0]
        matching_rows = df_ool[df_ool['VL_ObjectType'] == actual_object_type]
        print(f"\n5. All rows with ObjectType '{actual_object_type}':")
        for idx, row in matching_rows.iterrows():
            print(f"  Row {idx}: ObjectType='{row['VL_ObjectType']}', Description='{row['VL_Equipment_Description']}', Life Cycle='{row['VL_Life_Cycle']}'")
        
        # Check equipment description matches (ignoring ObjectType for now)
        print(f"\n6. Equipment description matching (across all ObjectTypes):")
        print(f"  Looking for: '{equipment_desc}'")
        
        # Search across all rows, not just matching ObjectType
        exact_match = df_ool[df_ool['VL_Equipment_Description'] == equipment_desc]
        if not exact_match.empty:
            print(f"  EXACT MATCH FOUND!")
            for idx, row in exact_match.iterrows():
                life_cycle = row['VL_Life_Cycle']
                object_type_in_ool = row['VL_ObjectType']
                print(f"  Row {idx}: ObjectType='{object_type_in_ool}', Life Cycle: {life_cycle}")
        else:
            print(f"  No exact match found. Checking for similar descriptions...")
            # Check for partial matches
            similar_matches = df_ool[df_ool['VL_Equipment_Description'].str.contains(equipment_desc, case=False, na=False)]
            if not similar_matches.empty:
                print(f"  Similar matches found:")
                for idx, row in similar_matches.iterrows():
                    print(f"    Row {idx}: '{row['VL_Equipment_Description']}' (ObjectType: {row['VL_ObjectType']}, Life Cycle: {row['VL_Life_Cycle']})")
            else:
                print(f"  No similar matches found either.")
                print(f"  All available equipment descriptions:")
                all_descriptions = df_ool['VL_Equipment_Description'].dropna().unique()
                for idx, desc in enumerate(all_descriptions[:20], 1):  # Show first 20
                    print(f"    {idx:2d}. '{desc}'")
                if len(all_descriptions) > 20:
                    print(f"    ... and {len(all_descriptions) - 20} more descriptions")

def main():
    """Main function to update equipment replacement schedules"""
    
    print("Equipment Replacement Schedule Updater")
    print("=" * 50)
    
    # Debug VV12205 first
    debug_equipment_lookup('VV12205')
    
    # Comment out examples for now as requested
    # # Example 1: Update single equipment
    # print("\nExample 1: Single Equipment Update")
    # equipment_id = 'VV12205'
    # new_year = 2027
    # 
    # print(f"Updating {equipment_id} to be replaced in {new_year}")
    # update_specific_equipment(equipment_id, new_year)
    # 
    # print("\n" + "=" * 50)
    # 
    # # Example 2: Update multiple equipment
    # print("\nExample 2: Multiple Equipment Update")
    # equipment_ids = ['VV12205', 'VV18683', 'VV18686', 'VV18702', 'VV18704']
    # new_year = 2026
    # 
    # print(f"Updating {len(equipment_ids)} equipment items to be replaced in {new_year}")
    # update_specific_equipment(equipment_ids, new_year)

if __name__ == "__main__":
    main()