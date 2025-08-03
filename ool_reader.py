import pandas as pd
import os

def read_ool_headers():
    """Read OOL.xlsx file and print its headers with multi-level structure"""
    try:
        # Check if file exists
        if not os.path.exists('OOL.xlsx'):
            print("Error: OOL.xlsx file not found in the current directory")
            return
        
        # Read the Excel file with multi-level headers
        print("Reading OOL.xlsx file...")
        
        # First, read with default settings to see structure
        df_default = pd.read_excel('OOL.xlsx')
        
        # Try reading with multi-level headers (first 2 rows as headers)
        df_multiheader = pd.read_excel('OOL.xlsx', header=[0, 1])
        
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
        df = pd.read_excel('OOL.xlsx', skiprows=2, header=None)
        
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
        # Read data.xlsx
        print("Reading data.xlsx...")
        df_data = pd.read_excel('data.xlsx')
        
        # Read OOL.xlsx with proper structure
        print("Reading OOL.xlsx...")
        df_ool = pd.read_excel('OOL.xlsx', skiprows=2, header=None)
        
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
        output_filename = 'data_updated.xlsx'
        df_data.to_excel(output_filename, index=False)
        print(f"\nSUCCESS: Updated data saved to {output_filename}")
        
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

if __name__ == "__main__":
    read_ool_headers()
    print("\n" + "="*50)
    read_ool_data_properly()
    print("\n" + "="*50)
    demo_equipment_update()