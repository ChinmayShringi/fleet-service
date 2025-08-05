#!/usr/bin/env python3
"""
Equipment Lifecycle Analysis Script
Reads equipment_lifecycle_by_business_unit.xlsx and extracts:
- Total Equipment from B2
- Life Cycle Distribution data
"""

import pandas as pd
import os
import sys
import json

def get_equipment_lifecycle_reference():
    """
    Analyze equipment lifecycle reference from the generated Excel file.
    Returns all equipment descriptions and their life cycles from B5 and C5 onwards.
    """
    try:
        # Get the equipment lifecycle reference file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        database_dir = os.path.join(os.path.dirname(script_dir), 'database')
        file_path = os.path.join(database_dir, 'equipment_lifecycle_reference.xlsx')
        
        print(f"Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'equipment_lifecycle_data': []
            }
        
        # Check available sheet names first
        xls = pd.ExcelFile(file_path)
        print(f"Available sheets: {xls.sheet_names}")
        
        # Try to find the correct sheet name
        sheet_name = None
        for name in xls.sheet_names:
            if 'lifecycle' in name.lower() or 'vehicle' in name.lower():
                sheet_name = name
                break
        
        if sheet_name is None:
            sheet_name = xls.sheet_names[0]  # Use first sheet if no match found
            
        print(f"Using sheet: '{sheet_name}'")
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        print(f"Sheet loaded with shape: {df.shape}")
        print("First few rows:")
        print(df.head(10))
        
        # Extract data from B5 and C5 onwards (rows 4+ in 0-indexed, columns 1 and 2)
        equipment_data = []
        
        # Start from row 5 (index 4) and get columns B and C (indices 1 and 2)
        for index in range(4, len(df)):  # Start from row 5 (0-indexed is 4)
            equipment_desc = df.iloc[index, 1]  # Column B
            life_cycle = df.iloc[index, 2]      # Column C
            
            # Skip empty rows
            if pd.isna(equipment_desc) and pd.isna(life_cycle):
                continue
                
            # Convert to string and clean up
            equipment_desc = str(equipment_desc) if not pd.isna(equipment_desc) else ""
            life_cycle = str(life_cycle) if not pd.isna(life_cycle) else ""
            
            # Skip if both are empty or 'nan'
            if equipment_desc.lower() in ['nan', ''] and life_cycle.lower() in ['nan', '']:
                continue
                
            equipment_data.append({
                'equipment_description': equipment_desc,
                'life_cycle': life_cycle,
                'row': index + 1  # 1-indexed row number for reference
            })
        
        print(f"Found {len(equipment_data)} equipment lifecycle entries")
        
        return {
            'success': True,
            'total_entries': len(equipment_data),
            'equipment_lifecycle_data': equipment_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'equipment_lifecycle_data': []
        }

def get_radio_equipment_cost_analysis():
    """
    Analyze radio equipment cost analysis from the generated Excel file.
    Returns LOB data with all column values from headers.
    """
    try:
        # Get the radio equipment cost analysis file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        database_dir = os.path.join(os.path.dirname(script_dir), 'database')
        file_path = os.path.join(database_dir, 'radio_equipment_cost_analysis.xlsx')
        
        print(f"Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'LOB': [],
                'values': {},
                'grand_total': {}
            }
        
        # Check available sheet names first
        xls = pd.ExcelFile(file_path)
        print(f"Available sheets: {xls.sheet_names}")
        
        # Try to find the correct sheet name - prefer Combined_Summary or similar
        sheet_name = None
        for name in xls.sheet_names:
            if 'combined' in name.lower() or 'summary' in name.lower():
                sheet_name = name
                break
        
        if sheet_name is None:
            # Fallback to sheets with 'radio' or 'cost'
            for name in xls.sheet_names:
                if 'radio' in name.lower() or 'cost' in name.lower():
                    sheet_name = name
                    break
        
        if sheet_name is None:
            sheet_name = xls.sheet_names[0]  # Use first sheet if no match found
            
        print(f"Using sheet: '{sheet_name}'")
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        print(f"Sheet loaded with shape: {df.shape}")
        print("First few rows:")
        print(df.head(10))
        
        # Find the header row (look for a row that has "LOB" and other column names)
        header_row_idx = None
        
        for idx in range(min(10, len(df))):  # Check first 10 rows for headers
            row = df.iloc[idx]
            # Convert to string and check if this looks like a header row
            if any('LOB' in str(cell).upper() for cell in row if not pd.isna(cell)):
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            header_row_idx = 0  # Fallback: assume first row is headers
        
        # Get actual headers from the row, excluding empty columns
        headers_row = df.iloc[header_row_idx]
        headers = []
        for i, cell in enumerate(headers_row):
            if not pd.isna(cell) and str(cell).strip():
                headers.append(str(cell).strip())
            elif headers:  # Only include empty cells if we already have headers
                headers.append(f"Column_{i}")
        
        print(f"Found headers at row {header_row_idx + 1}: {headers}")
        
        # Find LOB column in the actual DataFrame structure
        lob_col_idx = None
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[header_row_idx, col_idx]
            if not pd.isna(cell_value) and 'LOB' in str(cell_value).upper():
                lob_col_idx = col_idx
                break
        
        if lob_col_idx is None:
            lob_col_idx = 1  # Default to second column based on observed structure
        
        print(f"LOB column index in DataFrame: {lob_col_idx}")
        
        # Extract data starting from the row after headers
        data_start_row = header_row_idx + 1
        lob_values = []
        values_dict = {}
        grand_total = {}
        
        for row_idx in range(data_start_row, len(df)):
            row = df.iloc[row_idx]
            
            # Get LOB value from the LOB column
            lob_value = str(row.iloc[lob_col_idx]).strip()
            
            # Skip empty or 'nan' rows
            if pd.isna(row.iloc[lob_col_idx]) or lob_value.lower() in ['nan', '']:
                continue
            
            # Check if this is a Grand Total row
            is_grand_total = 'grand total' in lob_value.lower() or lob_value.lower() == 'total'
            
            # Skip other summary rows but capture Grand Total
            if ('total' in lob_value.lower() or lob_value.lower() == 'summary') and not is_grand_total:
                continue
            
            # Process data for this row
            row_data = {}
            data_col_start = lob_col_idx + 1  # Start after LOB column
            header_idx = 1  # Start from second header (skip "LOB")
            
            for col_idx in range(data_col_start, len(df.columns)):
                if header_idx < len(headers):
                    header = headers[header_idx]
                    
                    try:
                        cell_value = row.iloc[col_idx]
                        
                        # Handle different data types
                        if pd.isna(cell_value):
                            processed_value = 0
                        elif isinstance(cell_value, (int, float)):
                            processed_value = cell_value
                        else:
                            # Try to convert string to number
                            str_value = str(cell_value).strip().replace(',', '').replace('$', '')
                            try:
                                processed_value = float(str_value) if '.' in str_value else int(str_value)
                            except:
                                processed_value = str_value
                        
                        row_data[header] = processed_value
                        header_idx += 1
                        
                    except IndexError:
                        # Column doesn't exist for this row
                        row_data[header] = 0
                        header_idx += 1
            
            # Store in appropriate container
            if is_grand_total:
                grand_total = row_data
                print(f"📊 Captured Grand Total data")
            else:
                lob_values.append(lob_value)
                values_dict[lob_value] = row_data
        
        print(f"Found {len(lob_values)} LOB entries")
        print(f"Headers: {headers}")
        
        return {
            'success': True,
            'LOB': lob_values,
            'headers': headers,
            'values': values_dict,
            'grand_total': grand_total,
            'total_lob_count': len(lob_values)
        }
        
    except Exception as e:
        print(f"❌ Error in radio equipment cost analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'LOB': [],
            'values': {},
            'grand_total': {}
        }

def get_vehicle_replacement_by_category_analysis():
    """
    Analyze vehicle replacement by category from the generated Excel file.
    Returns category data with all column values from headers.
    """
    try:
        # Get the vehicle replacement by category file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        database_dir = os.path.join(os.path.dirname(script_dir), 'database')
        file_path = os.path.join(database_dir, 'vehicle_replacement_by_category.xlsx')
        
        print(f"Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'Categories': [],
                'values': {},
                'grand_total': {}
            }
        
        # Check available sheet names first
        xls = pd.ExcelFile(file_path)
        print(f"Available sheets: {xls.sheet_names}")
        
        # Try to find the correct sheet name - prefer first sheet or one with relevant keywords
        sheet_name = None
        for name in xls.sheet_names:
            if any(keyword in name.lower() for keyword in ['vehicle', 'replacement', 'category', 'summary']):
                sheet_name = name
                break
        
        if sheet_name is None:
            sheet_name = xls.sheet_names[0]  # Use first sheet if no match found
            
        print(f"Using sheet: '{sheet_name}'")
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        print(f"Sheet loaded with shape: {df.shape}")
        print("First few rows:")
        print(df.head(10))
        
        # Find the header row (look for a row that has category/vehicle related headers)
        header_row_idx = None
        
        for idx in range(min(10, len(df))):  # Check first 10 rows for headers
            row = df.iloc[idx]
            # Convert to string and check if this looks like a header row
            row_str = [str(cell).strip().lower() for cell in row if not pd.isna(cell)]
            if any(keyword in ' '.join(row_str) for keyword in ['category', 'vehicle', 'type', 'class']):
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            header_row_idx = 0  # Fallback: assume first row is headers
        
        # Get actual headers from the row, excluding empty columns
        headers_row = df.iloc[header_row_idx]
        headers = []
        for i, cell in enumerate(headers_row):
            if not pd.isna(cell) and str(cell).strip():
                headers.append(str(cell).strip())
            elif headers:  # Only include empty cells if we already have headers
                headers.append(f"Column_{i}")
        
        print(f"Found headers at row {header_row_idx + 1}: {headers}")
        
        # Find category column in the actual DataFrame structure
        category_col_idx = None
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[header_row_idx, col_idx]
            if not pd.isna(cell_value):
                cell_str = str(cell_value).strip().lower()
                if any(keyword in cell_str for keyword in ['category', 'vehicle', 'type', 'class']):
                    category_col_idx = col_idx
                    break
        
        if category_col_idx is None:
            category_col_idx = 0  # Default to first column
        
        print(f"Category column index in DataFrame: {category_col_idx}")
        
        # Extract data starting from the row after headers
        data_start_row = header_row_idx + 1
        category_values = []
        values_dict = {}
        grand_total = {}
        
        for row_idx in range(data_start_row, len(df)):
            row = df.iloc[row_idx]
            
            # Get category value from the category column
            category_value = str(row.iloc[category_col_idx]).strip()
            
            # Skip empty or 'nan' rows
            if pd.isna(row.iloc[category_col_idx]) or category_value.lower() in ['nan', '']:
                continue
            
            # Check if this is a Grand Total row
            is_grand_total = 'grand total' in category_value.lower() or category_value.lower() == 'total'
            
            # Skip other summary rows but capture Grand Total
            if ('total' in category_value.lower() or category_value.lower() == 'summary') and not is_grand_total:
                continue
            
            # Process data for this row
            row_data = {}
            data_col_start = category_col_idx + 1  # Start after category column
            header_idx = 1  # Start from second header (skip category header)
            
            for col_idx in range(data_col_start, len(df.columns)):
                if header_idx < len(headers):
                    header = headers[header_idx]
                    
                    try:
                        cell_value = row.iloc[col_idx]
                        
                        # Handle different data types
                        if pd.isna(cell_value):
                            processed_value = 0
                        elif isinstance(cell_value, (int, float)):
                            processed_value = cell_value
                        else:
                            # Try to convert string to number
                            str_value = str(cell_value).strip().replace(',', '').replace('$', '')
                            try:
                                processed_value = float(str_value) if '.' in str_value else int(str_value)
                            except:
                                processed_value = str_value
                        
                        row_data[header] = processed_value
                        header_idx += 1
                        
                    except IndexError:
                        # Column doesn't exist for this row
                        row_data[header] = 0
                        header_idx += 1
            
            # Store in appropriate container
            if is_grand_total:
                grand_total = row_data
                print(f"📊 Captured Grand Total data")
            else:
                category_values.append(category_value)
                values_dict[category_value] = row_data
        
        print(f"Found {len(category_values)} category entries")
        print(f"Headers: {headers}")
        
        return {
            'success': True,
            'Categories': category_values,
            'headers': headers,
            'values': values_dict,
            'grand_total': grand_total,
            'total_category_count': len(category_values)
        }
        
    except Exception as e:
        print(f"❌ Error in vehicle replacement by category analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'Categories': [],
            'values': {},
            'grand_total': {}
        }

def get_vehicle_replacement_detailed_forecast_analysis():
    """
    Analyze vehicle replacement detailed forecast from the generated Excel file.
    Returns LOB data with only total rows organized by total type.
    """
    try:
        # Get the vehicle replacement detailed forecast file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        database_dir = os.path.join(os.path.dirname(script_dir), 'database')
        file_path = os.path.join(database_dir, 'vehicle_replacement_detailed_forecast.xlsx')
        
        print(f"Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'LOB': [],
                'data': {}
            }
        
        # Check available sheet names first
        xls = pd.ExcelFile(file_path)
        print(f"Available sheets: {xls.sheet_names}")
        
        # Process each sheet to find LOB data
        lob_data = {}
        all_lobs = []
        
        for sheet_name in xls.sheet_names:
            print(f"\nProcessing sheet: '{sheet_name}'")
            
            # Read the Excel sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            print(f"Sheet loaded with shape: {df.shape}")
            print("First few rows:")
            print(df.head(10))
            
            # Find the header row (look for a row that has vehicle/count/cost related headers)
            header_row_idx = None
            headers = []
            
            for idx in range(min(15, len(df))):  # Check first 15 rows for headers
                row = df.iloc[idx]
                # Convert to string and check if this looks like a header row
                row_str = [str(cell).strip().lower() for cell in row if not pd.isna(cell)]
                if any(keyword in ' '.join(row_str) for keyword in ['vehicle count', 'replacement cost', '2026', '2027']):
                    header_row_idx = idx
                    # Get actual headers from the row, excluding empty columns
                    headers_row = df.iloc[idx]
                    headers = []
                    for i, cell in enumerate(headers_row):
                        if not pd.isna(cell) and str(cell).strip():
                            headers.append(str(cell).strip())
                        elif headers:  # Only include empty cells if we already have headers
                            headers.append(f"Column_{i}")
                    break
            
            if header_row_idx is None:
                print(f"⚠️ No headers found in sheet {sheet_name}, skipping")
                continue
            
            print(f"Found headers at row {header_row_idx + 1}: {headers}")
            
            # Extract data starting from the row after headers
            data_start_row = header_row_idx + 1
            
            # Look for total rows and organize by LOB
            current_lob = None
            lob_totals = {}
            grand_total = None
            
            for row_idx in range(data_start_row, len(df)):
                row = df.iloc[row_idx]
                
                # Get first column value
                first_col_value = str(row.iloc[0]).strip()
                
                # Skip empty or 'nan' rows
                if pd.isna(row.iloc[0]) or first_col_value.lower() in ['nan', '']:
                    continue
                
                # Check if this is a LOB name (no "total" in it, not indented)
                if 'total' not in first_col_value.lower() and not first_col_value.startswith(' '):
                    # This might be a LOB name if it's in our known LOBs
                    known_lobs = ['DP&C', 'UOS', 'CUSTOMER OPS', 'ELEC OPERATIONS', 'GAS OPERATIONS', 'SERVICE CORP']
                    if first_col_value in known_lobs:
                        current_lob = first_col_value
                        if current_lob not in lob_totals:
                            lob_totals[current_lob] = {}
                        print(f"📍 Found LOB: {current_lob}")
                    continue
                
                # Check if this row contains "total" in the first column
                if 'total' not in first_col_value.lower():
                    continue
                
                print(f"Found total row: '{first_col_value}'")
                
                # Extract data for this total row
                row_data = {}
                for col_idx, header in enumerate(headers):
                    if col_idx == 0:
                        continue  # Skip first column (contains the total type)
                    
                    try:
                        cell_value = row.iloc[col_idx]
                        
                        # Handle different data types
                        if pd.isna(cell_value):
                            processed_value = 0
                        elif isinstance(cell_value, (int, float)):
                            processed_value = cell_value
                        else:
                            # Try to convert string to number
                            str_value = str(cell_value).strip().replace(',', '').replace('$', '')
                            try:
                                processed_value = float(str_value) if '.' in str_value else int(str_value)
                            except:
                                processed_value = str_value
                        
                        row_data[header] = processed_value
                        
                    except IndexError:
                        # Column doesn't exist for this row
                        row_data[header] = 0
                
                # Determine how to store this total
                if first_col_value == "Grand Total":
                    grand_total = row_data
                elif current_lob and (first_col_value == f"{current_lob} Total"):
                    # This is the main LOB total
                    lob_totals[current_lob]["Total"] = row_data
                elif current_lob and first_col_value in ["H Total", "L Total", "P Total"]:
                    # This is a vehicle class total within the current LOB
                    lob_totals[current_lob][first_col_value] = row_data
                else:
                    # Handle any other total types
                    if current_lob:
                        lob_totals[current_lob][first_col_value] = row_data
            
            # Store the organized data
            if lob_totals:
                all_lobs.extend(list(lob_totals.keys()))
                lob_data.update(lob_totals)
                
                # Add grand total if found
                if grand_total:
                    lob_data["Grand Total"] = {"Grand Total": grand_total}
                
                print(f"✅ Found {len(lob_totals)} LOBs with totals")
        
        print(f"\nFound {len(all_lobs)} LOBs: {all_lobs}")
        print(f"LOB data keys: {list(lob_data.keys())}")
        
        return {
            'success': True,
            'LOB': all_lobs,
            'data': lob_data,
            'grand_total': lob_data.get("Grand Total", {}),
            'total_lob_count': len(all_lobs)
        }
        
    except Exception as e:
        print(f"❌ Error in vehicle replacement detailed forecast analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'LOB': [],
            'data': {}
        }

def get_equipment_lifecycle_analysis():
    """
    Analyze equipment lifecycle by business unit from the generated Excel file.
    Returns total equipment count and lifecycle distribution data.
    """
    try:
        # Get the equipment lifecycle file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        database_dir = os.path.join(os.path.dirname(script_dir), 'database')
        file_path = os.path.join(database_dir, 'equipment_lifecycle_by_business_unit.xlsx')
        
        print(f"Looking for file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'Equipment lifecycle file not found: {file_path}',
                'total_equipment': 0,
                'lifecycle_distribution': []
            }
            
        print(f"File found! Reading Excel file...")
        
        # Read the Excel file - try common sheet names
        sheet_names_to_try = ['Sheet1', 'Equipment_Lifecycle', 'LOB Equipment Lifecycle', 'Summary']
        df = None
        
        for sheet_name in sheet_names_to_try:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                print(f"Successfully read sheet: {sheet_name}")
                break
            except Exception as e:
                print(f"Failed to read sheet '{sheet_name}': {e}")
                continue
        
        # If all specific sheet names fail, try reading the first sheet
        if df is None:
            try:
                df = pd.read_excel(file_path, sheet_name=0, header=None)
                print("Successfully read first sheet")
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Could not read Excel file: {str(e)}',
                    'total_equipment': 0,
                    'lifecycle_distribution': []
                }
        
        print(f"DataFrame shape: {df.shape}")
        print(f"First few rows:")
        print(df.head(10))
        
        # Extract total equipment from B2 (row 1, column 1 in 0-indexed)
        total_equipment = 0
        try:
            if len(df) > 1 and len(df.columns) > 1:
                total_equipment_raw = df.iloc[1, 1]  # B2 cell
                print(f"Raw B2 value: {total_equipment_raw} (type: {type(total_equipment_raw)})")
                
                if pd.isna(total_equipment_raw):
                    total_equipment = 0
                else:
                    total_equipment = int(total_equipment_raw)
                    
                print(f"Total equipment extracted: {total_equipment}")
            else:
                print("DataFrame too small to extract B2")
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not extract total equipment from B2: {e}")
            total_equipment = 0
        
        # Find "Life Cycle Distribution:" and extract data after it
        lifecycle_distribution = []
        try:
            print(f"\nSearching for 'Life Cycle Distribution:' in column A...")
            
            # Search for "Life Cycle Distribution:" in column A
            lifecycle_start_row = None
            for idx, row in df.iterrows():
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    cell_value = str(row.iloc[0]).strip()
                    print(f"Row {idx}, Col A: '{cell_value}'")
                    
                    if "Life Cycle Distribution:" in cell_value:
                        lifecycle_start_row = idx
                        print(f"✅ Found 'Life Cycle Distribution:' at row {idx}")
                        break
            
            if lifecycle_start_row is not None:
                print(f"\nExtracting data after row {lifecycle_start_row}...")
                
                # Extract data after "Life Cycle Distribution:"
                for idx in range(lifecycle_start_row + 1, len(df)):
                    row = df.iloc[idx]
                    
                    # Debug: print row data
                    print(f"Row {idx}: {row.tolist()[:3]}")  # Print first 3 columns
                    
                    # Check if we have data in both columns A and B
                    if len(row) >= 2 and pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        years_str = str(row.iloc[0]).strip()
                        count_value = row.iloc[1]
                        
                        print(f"  Processing: '{years_str}' = {count_value}")
                        
                        # Skip empty rows or header-like content
                        if not years_str or years_str == "" or "equipment items" in years_str.lower():
                            print(f"  Skipping: empty or header-like")
                            continue
                            
                        # Extract the lifecycle info
                        try:
                            count = int(count_value)
                            lifecycle_entry = {
                                'lifecycle': years_str,
                                'count': count
                            }
                            lifecycle_distribution.append(lifecycle_entry)
                            print(f"  ✅ Added: {lifecycle_entry}")
                        except (ValueError, TypeError) as e:
                            print(f"  ❌ Could not parse count '{count_value}': {e}")
                            continue
                    else:
                        # If we hit empty rows, we might be done with the distribution
                        if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]):
                            print(f"  Hit empty row at {idx}, continuing...")
                            continue
                        else:
                            print(f"  Row {idx} incomplete data")
                            
            else:
                print("❌ 'Life Cycle Distribution:' not found in column A")
                
        except Exception as e:
            print(f"Warning: Could not extract lifecycle distribution: {e}")
        
        result = {
            'success': True,
            'total_equipment': total_equipment,
            'lifecycle_distribution': lifecycle_distribution,
            'file_path': file_path
        }
        
        print(f"\n🎉 Analysis complete!")
        print(f"Total Equipment: {total_equipment}")
        print(f"Lifecycle entries found: {len(lifecycle_distribution)}")
        
        return result
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Error analyzing equipment lifecycle: {str(e)}',
            'total_equipment': 0,
            'lifecycle_distribution': []
        }
        print(f"❌ Error: {error_result}")
        return error_result

if __name__ == "__main__":
    print("=== Equipment Lifecycle Analysis ===")
    result1 = get_equipment_lifecycle_analysis()
    print(json.dumps(result1, indent=2))
    
    print("\n" + "="*50)
    print("=== Equipment Lifecycle Reference ===")
    result2 = get_equipment_lifecycle_reference()
    print(json.dumps(result2, indent=2))
    
    print("\n" + "="*50)
    print("=== Radio Equipment Cost Analysis ===")
    result3 = get_radio_equipment_cost_analysis()
    print(json.dumps(result3, indent=2))
    
    print("\n" + "="*50)
    print("=== Vehicle Replacement by Category Analysis ===")
    result4 = get_vehicle_replacement_by_category_analysis()
    print(json.dumps(result4, indent=2))
    
    print("\n" + "="*50)
    print("=== Vehicle Replacement Detailed Forecast Analysis ===")
    result5 = get_vehicle_replacement_detailed_forecast_analysis()
    print(json.dumps(result5, indent=2))
