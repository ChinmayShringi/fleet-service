import pandas as pd
import shutil
import os
from constants.file_constants import get_input_file_safe, get_output_file, get_sheet_name, ensure_database_directory

def calculate_vehicle_data():
    """Calculate vehicle counts and replacement costs for H, L, P categories from data.xlsx for years 2026-2035"""
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Initialize dictionaries to store results for all years
    years = range(2026, 2036)  # 2026 to 2035
    counts = {'H': {}, 'L': {}, 'P': {}}
    costs = {'H': {}, 'L': {}, 'P': {}}
    
    print("=== Vehicle Data Calculation for 10-Year Plan (2026-2035) ===\n")
    
    for year in years:
        forecast_col = f'{year} Forecast Count'
        replacement_cost_col = f'{year} Replacement Cost'
        
        # Check if columns exist in data
        if forecast_col not in df_data.columns or replacement_cost_col not in df_data.columns:
            print(f"Warning: Missing columns for year {year}")
            continue
            
        # Calculate counts for each vehicle class where [year] Forecast Count = 1
        forecast_condition = df_data[forecast_col] == 1
        
        count_H = len(df_data[(forecast_condition) & (df_data['L.H.P'] == 'H')])
        count_L = len(df_data[(forecast_condition) & (df_data['L.H.P'] == 'L')])
        count_P = len(df_data[(forecast_condition) & (df_data['L.H.P'] == 'P')])
        
        # Calculate replacement costs for each vehicle class where [year] Forecast Count = 1
        cost_H = df_data[(forecast_condition) & (df_data['L.H.P'] == 'H')][replacement_cost_col].fillna(0).sum()
        cost_L = df_data[(forecast_condition) & (df_data['L.H.P'] == 'L')][replacement_cost_col].fillna(0).sum()
        cost_P = df_data[(forecast_condition) & (df_data['L.H.P'] == 'P')][replacement_cost_col].fillna(0).sum()
        
        # Store results
        counts['H'][year] = count_H
        counts['L'][year] = count_L
        counts['P'][year] = count_P
        costs['H'][year] = cost_H
        costs['L'][year] = cost_L
        costs['P'][year] = cost_P
        
        print(f"{year} - Vehicle Counts (Forecast = 1): H={count_H}, L={count_L}, P={count_P}, Total={count_H + count_L + count_P}")
        print(f"{year} - Replacement Costs: H=${cost_H:,.2f}, L=${cost_L:,.2f}, P=${cost_P:,.2f}, Total=${cost_H + cost_L + cost_P:,.2f}")
        print()
    
    return counts, costs

def create_ev_assumption_pivot_table():
    """Create EV_ASSUMPTION analysis using pivot tables with template column names"""
    
    # Calculate the vehicle counts and replacement costs for all years
    counts, costs = calculate_vehicle_data()
    
    # Get radio installation expense data
    radio_results = analyze_radio_installation_by_lob()
    
    print("=== Creating EV_ASSUMPTION Pivot Table ===")
    
    # Create pivot data
    years = range(2026, 2036)
    vehicle_classes = ['H', 'L', 'P']
    
    # Create combined summary with template column names
    combined_data = []
    
    for vehicle_class in vehicle_classes:
        row_data = {'Vehicle Class': vehicle_class}
        for year in years:
            if year in counts[vehicle_class]:
                count = counts[vehicle_class][year]
                cost = costs[vehicle_class][year]
                row_data[f'{year} Vehicle Count'] = count
                row_data[f'{year} Replacement Cost (Est.)'] = cost
            else:
                row_data[f'{year} Vehicle Count'] = 0
                row_data[f'{year}'] = 0
        combined_data.append(row_data)
    
    ev_pivot = pd.DataFrame(combined_data)
    
    # Add Grand Total row
    grand_total_row = {'Vehicle Class': 'Grand Total'}
    for year in years:
        total_count = sum(counts[vc].get(year, 0) for vc in vehicle_classes)
        total_cost = sum(costs[vc].get(year, 0) for vc in vehicle_classes)
        grand_total_row[f'{year} Vehicle Count'] = total_count
        grand_total_row[f'{year} Replacement Cost (Est.)'] = total_cost
    
    # Add grand total as the last row
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([grand_total_row])], ignore_index=True)
    
    # Add Radio Installation Expense row
    radio_expense_row = {'Vehicle Class': 'Radio Installation Expense'}
    for year in years:
        # Calculate grand total radio spend for this year
        total_radio_spend = 0
        for lob, data in radio_results.items():
            if year in data['spends']:
                total_radio_spend += data['spends'][year]
        
        radio_expense_row[f'{year} Vehicle Count'] = 0  # No vehicle count for radio expense
        radio_expense_row[f'{year} Replacement Cost (Est.)'] = total_radio_spend
    
    # Add radio expense row after grand total
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([radio_expense_row])], ignore_index=True)
    
    # Add Total pre EV with Radio Installs row (Grand Total + Radio Expense)
    total_pre_ev_row = {'Vehicle Class': 'Total pre EV with Radio Installs'}
    for year in years:
        # Vehicle count is same as Grand Total (radio expense has 0 count)
        total_count = sum(counts[vc].get(year, 0) for vc in vehicle_classes)
        
        # Cost is Grand Total + Radio Installation Expense
        grand_total_cost = sum(costs[vc].get(year, 0) for vc in vehicle_classes)
        radio_expense_cost = 0
        for lob, data in radio_results.items():
            if year in data['spends']:
                radio_expense_cost += data['spends'][year]
        
        total_pre_ev_cost = grand_total_cost + radio_expense_cost
        
        total_pre_ev_row[f'{year} Vehicle Count'] = total_count
        total_pre_ev_row[f'{year} Replacement Cost (Est.)'] = total_pre_ev_cost
    
    # Add total pre EV row after radio expense
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([total_pre_ev_row])], ignore_index=True)
    
    # Add 2 padding rows at the top
    padding_row_1 = {'Vehicle Class': ''}
    padding_row_2 = {'Vehicle Class': ''}
    for year in years:
        padding_row_1[f'{year} Vehicle Count'] = 0
        padding_row_1[f'{year} Replacement Cost (Est.)'] = 0
        padding_row_2[f'{year} Vehicle Count'] = 0
        padding_row_2[f'{year} Replacement Cost (Est.)'] = 0
    
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([padding_row_1])], ignore_index=True)
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([padding_row_2])], ignore_index=True)
    
    # Get EV impact values from dedicated analyses for the new rows
    print("  Calculating EV impact values from dedicated analyses...")
    
    # Get Freightliner (H) EV impact values
    freightliner_data = create_freightliner_analysis_data()
    freightliner_df = pd.DataFrame(freightliner_data)
    
    # Get Light vehicle EV impact values
    van_data = create_van_ev_analysis_data()
    car_suv_data = create_car_suv_ev_analysis_data()  
    pickup_data = create_pickup_ev_analysis_data()
    
    van_df = pd.DataFrame(van_data)
    car_suv_df = pd.DataFrame(car_suv_data)
    pickup_df = pd.DataFrame(pickup_data)
    
    # Find EV Premium Impact rows in each analysis
    freightliner_impact_row = freightliner_df[freightliner_df['Vehicle Class'] == 'EV Premium Impact to Budget']
    van_impact_row = van_df[van_df['Vehicle Class'] == 'EV Premium Impact to Budget']
    car_suv_impact_row = car_suv_df[car_suv_df['Vehicle Class'] == 'EV Premium Impact to Budget']
    pickup_impact_row = pickup_df[pickup_df['Vehicle Class'] == 'EV Premium Impact to Budget']
    
    # Add the 5 new EV-related rows with calculated values
    ev_rows = [
        'H -EV Purchases Net Impact to Capital Budget',
        'L - EV Purchased Net Impact to Capital Budget', 
        'Adjusted Budget to Reflect Avg EV Incremental',
        '3_14 update',
        'Var'
    ]
    
    for i, row_name in enumerate(ev_rows):
        ev_row = {'Vehicle Class': row_name}
        
        for year in years:
            if i == 0:  # H -EV Purchases Net Impact to Capital Budget
                # Get Freightliner EV Premium Impact value for this year
                ev_row[f'{year} Vehicle Count'] = 0
                if not freightliner_impact_row.empty:
                    ev_row[f'{year} Replacement Cost (Est.)'] = freightliner_impact_row.iloc[0].get(f'{year}', 0)
                else:
                    ev_row[f'{year} Replacement Cost (Est.)'] = 0
                
            elif i == 1:  # L - EV Purchased Net Impact to Capital Budget  
                # Sum of Van + Car/SUV + Pickup EV Premium Impact values (taking magnitude)
                van_impact = abs(van_impact_row.iloc[0].get(f'{year}', 0)) if not van_impact_row.empty else 0
                car_suv_impact = abs(car_suv_impact_row.iloc[0].get(f'{year}', 0)) if not car_suv_impact_row.empty else 0
                pickup_impact = abs(pickup_impact_row.iloc[0].get(f'{year}', 0)) if not pickup_impact_row.empty else 0
                
                total_light_impact = van_impact + car_suv_impact + pickup_impact
                ev_row[f'{year} Vehicle Count'] = 0
                ev_row[f'{year} Replacement Cost (Est.)'] = total_light_impact
                
            elif i == 2:  # Adjusted Budget to Reflect Avg EV Incremental
                # Vehicle Count = same as "Total pre EV with Radio Installs"
                # Find the "Total pre EV with Radio Installs" row value
                total_pre_ev_count = 0
                total_pre_ev_cost = 0
                for prev_idx, prev_row_data in enumerate(ev_pivot.to_dict('records')):
                    if prev_row_data.get('Vehicle Class') == 'Total pre EV with Radio Installs':
                        total_pre_ev_count = prev_row_data.get(f'{year} Vehicle Count', 0)
                        total_pre_ev_cost = prev_row_data.get(f'{year} Replacement Cost (Est.)', 0)
                        break
                
                # Get H and L EV impact values we just calculated
                h_ev_impact = 0
                l_ev_impact = 0
                if not freightliner_impact_row.empty:
                    h_ev_impact = freightliner_impact_row.iloc[0].get(f'{year}', 0)
                if len(ev_rows) > 1:  # L row exists
                    van_impact = abs(van_impact_row.iloc[0].get(f'{year}', 0)) if not van_impact_row.empty else 0
                    car_suv_impact = abs(car_suv_impact_row.iloc[0].get(f'{year}', 0)) if not car_suv_impact_row.empty else 0
                    pickup_impact = abs(pickup_impact_row.iloc[0].get(f'{year}', 0)) if not pickup_impact_row.empty else 0
                    l_ev_impact = van_impact + car_suv_impact + pickup_impact
                
                ev_row[f'{year} Vehicle Count'] = total_pre_ev_count
                ev_row[f'{year} Replacement Cost (Est.)'] = total_pre_ev_cost + h_ev_impact + l_ev_impact
                
            else:
                # Placeholder values for other rows
                ev_row[f'{year} Vehicle Count'] = 0
                ev_row[f'{year} Replacement Cost (Est.)'] = 0
        
        ev_pivot = pd.concat([ev_pivot, pd.DataFrame([ev_row])], ignore_index=True)
    
    # Add 2 padding rows at the bottom
    padding_row_3 = {'Vehicle Class': ''}
    padding_row_4 = {'Vehicle Class': ''}
    for year in years:
        padding_row_3[f'{year} Vehicle Count'] = 0
        padding_row_3[f'{year} Replacement Cost (Est.)'] = 0
        padding_row_4[f'{year} Vehicle Count'] = 0
        padding_row_4[f'{year} Replacement Cost (Est.)'] = 0
    
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([padding_row_3])], ignore_index=True)
    ev_pivot = pd.concat([ev_pivot, pd.DataFrame([padding_row_4])], ignore_index=True)
    
    # Create output directory if it doesn't exist
    ensure_database_directory()
    
    # Save the EV assumption pivot table to output folder
    output_path = get_output_file("ELECTRIC_VEHICLE_BUDGET_ANALYSIS")
    
    # Individual EV analyses will be in separate sheets to avoid column format conflicts
    print("\nPreparing individual EV analyses for separate sheets...")
    
    # Create individual analysis DataFrames
    print("  Creating Freightliner EV Analysis...")
    freightliner_data = create_freightliner_analysis_data()
    freightliner_df = pd.DataFrame(freightliner_data)
    
    print("  Creating Van EV Analysis...")
    van_data = create_van_ev_analysis_data()
    van_df = pd.DataFrame(van_data)
    
    print("  Creating Car/SUV EV Analysis...")
    car_suv_data = create_car_suv_ev_analysis_data()
    car_suv_df = pd.DataFrame(car_suv_data)
    
    print("  Creating Pickup EV Analysis...")
    pickup_data = create_pickup_ev_analysis_data()
    pickup_df = pd.DataFrame(pickup_data)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main EV Summary sheet (clean format without mixed columns)
        ev_pivot.to_excel(writer, sheet_name=get_sheet_name('EV_SUMMARY'), index=False)
        
        # Individual EV analyses in separate sheets (with their own format)
        freightliner_df.to_excel(writer, sheet_name=get_sheet_name('FREIGHTLINER_EV'), index=False)
        van_df.to_excel(writer, sheet_name=get_sheet_name('VAN_EV'), index=False)
        car_suv_df.to_excel(writer, sheet_name=get_sheet_name('CAR_SUV_EV'), index=False)
        pickup_df.to_excel(writer, sheet_name=get_sheet_name('PICKUP_EV'), index=False)
        
        # Also create separate pivot tables for counts and costs
        count_data = []
        cost_data = []
        
        for vehicle_class in vehicle_classes:
            count_row = {'Vehicle Class': vehicle_class}
            cost_row = {'Vehicle Class': vehicle_class}
            for year in years:
                count_row[str(year)] = counts[vehicle_class].get(year, 0)
                cost_row[str(year)] = costs[vehicle_class].get(year, 0)
            count_data.append(count_row)
            cost_data.append(cost_row)
        
        # Add grand totals
        count_grand = {'Vehicle Class': 'Grand Total'}
        cost_grand = {'Vehicle Class': 'Grand Total'}
        for year in years:
            count_grand[str(year)] = sum(counts[vc].get(year, 0) for vc in vehicle_classes)
            cost_grand[str(year)] = sum(costs[vc].get(year, 0) for vc in vehicle_classes)
        count_data.append(count_grand)
        cost_data.append(cost_grand)
        
        pd.DataFrame(count_data).to_excel(writer, sheet_name=get_sheet_name('VEHICLE_COUNTS'), index=False)
        pd.DataFrame(cost_data).to_excel(writer, sheet_name=get_sheet_name('REPLACEMENT_COSTS'), index=False)
    
    
    for i, vehicle_class in enumerate(vehicle_classes + ['Grand Total', 'Radio Installation Expense', 'Total pre EV with Radio Installs']):
        row = f"{vehicle_class:<28}"
        for year in range(2026, 2031):
            if vehicle_class == 'Grand Total':
                count = sum(counts[vc].get(year, 0) for vc in vehicle_classes)
                cost = sum(costs[vc].get(year, 0) for vc in vehicle_classes)
                row += f" | {count}/{cost:,.0f}"
            elif vehicle_class == 'Radio Installation Expense':
                # Calculate radio expense for this year
                radio_spend = 0
                for lob, data in radio_results.items():
                    if year in data['spends']:
                        radio_spend += data['spends'][year]
                row += f" | 0/{radio_spend:,.0f}"
            elif vehicle_class == 'Total pre EV with Radio Installs':
                # Calculate total pre EV (Grand Total + Radio Expense)
                count = sum(counts[vc].get(year, 0) for vc in vehicle_classes)
                grand_total_cost = sum(costs[vc].get(year, 0) for vc in vehicle_classes)
                radio_spend = 0
                for lob, data in radio_results.items():
                    if year in data['spends']:
                        radio_spend += data['spends'][year]
                total_cost = grand_total_cost + radio_spend
                row += f" | {count}/{total_cost:,.0f}"
            else:
                count = counts[vehicle_class].get(year, 0)
                cost = costs[vehicle_class].get(year, 0)
                row += f" | {count}/{cost:,.0f}"
        print(row)
    
    print("\nNotes:")
    print("- Radio Installation Expense copied from Radio_Installation_Analysis grand totals")
    print("- Total pre EV with Radio Installs = Grand Total + Radio Installation Expense")
    
    return output_path

def analyze_radio_installation_by_lob():
    """Analyze Radio Installation Expense by LOB using pivot tables"""
    
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    print("=== Radio Installation Expense Analysis ===\n")
    
    # Get unique LOB values
    lob_values = df_data['LOB from Location'].value_counts()
    print("Available LOB from Location values:")
    for lob, count in lob_values.items():
        print(f"  {lob}: {count} records")
    
    # Years for radio analysis
    years = range(2026, 2036)
    
    # Initialize results dictionary
    radio_results = {}
    
    # Analyze each LOB
    for lob in lob_values.index:
        if pd.isna(lob) or lob == '#REF!':
            continue  # Skip invalid LOB values
            
        print(f"\n=== Analysis for {lob} ===")
        
        # Filter data for this LOB
        lob_data = df_data[df_data['LOB from Location'] == lob]
        
        radio_results[lob] = {'counts': {}, 'spends': {}}
        
        for year in years:
            radio_count_col = f'{year} Radio Count'
            radio_spend_col = f'{year} Radio Spend'
            
            if radio_count_col not in df_data.columns or radio_spend_col not in df_data.columns:
                continue
            
            # Filter where Radio Count = 1
            radio_filter = lob_data[radio_count_col] == 1
            filtered_data = lob_data[radio_filter]
            
            # Count of records where Radio Count = 1
            radio_count = len(filtered_data)
            
            # Sum of Radio Spend where Radio Count = 1
            radio_spend = filtered_data[radio_spend_col].fillna(0).sum()
            
            radio_results[lob]['counts'][year] = radio_count
            radio_results[lob]['spends'][year] = radio_spend
            
            print(f"  {year}: Count={radio_count}, Spend=${radio_spend:,.2f}")
    
    return radio_results

def create_radio_pivot_table():
    """Create pivot table for Radio Installation analysis"""
    
    # Get the radio analysis results
    radio_results = analyze_radio_installation_by_lob()
    
    print("\n=== Creating Radio Installation Pivot Table ===")
    
    # Create pivot table data
    pivot_data = []
    years = range(2026, 2036)
    
    for lob, data in radio_results.items():
        for year in years:
            if year in data['counts'] and year in data['spends']:
                pivot_data.append({
                    'LOB': lob,
                    'Year': year,
                    'Radio_Count': data['counts'][year],
                    'Radio_Spend': data['spends'][year]
                })
    
    # Create DataFrame
    df_pivot = pd.DataFrame(pivot_data)
    
    if not df_pivot.empty:
        # Create pivot tables
        count_pivot = df_pivot.pivot(index='LOB', columns='Year', values='Radio_Count').fillna(0)
        spend_pivot = df_pivot.pivot(index='LOB', columns='Year', values='Radio_Spend').fillna(0)
        
        print("\nRadio Count Pivot Table:")
        print(count_pivot)
        
        print("\nRadio Spend Pivot Table:")
        print(spend_pivot)
        
        # Create combined pivot table showing both count and spend
        print("\n=== COMBINED RADIO INSTALLATION SUMMARY ===")
        print("LOB | Year | Count | Spend")
        print("-" * 50)
        
        for lob in count_pivot.index:
            print(f"\n{lob}:")
            for year in count_pivot.columns:
                count = int(count_pivot.loc[lob, year])
                spend = spend_pivot.loc[lob, year]
                if count > 0 or spend > 0:
                    print(f"  {year}: {count} radios, ${spend:,.0f}")
        
        # Create a user-friendly summary table for key years
        print("\n=== 2026-2030 SUMMARY TABLE ===")
        key_years = [2026, 2027, 2028, 2029, 2030]
        print("LOB" + "".join([f" | {year}" for year in key_years]))
        print("-" * (15 + 15 * len(key_years)))
        
        for lob in count_pivot.index:
            row = f"{lob:<12}"
            for year in key_years:
                if year in count_pivot.columns:
                    count = int(count_pivot.loc[lob, year])
                    spend = spend_pivot.loc[lob, year]
                    if count > 0:
                        row += f" | {count}/${spend:,.0f}"
                    else:
                        row += f" | 0/$0"
                else:
                    row += f" | 0/$0"
            print(row)
        
        # Add grand totals row
        print("-" * (15 + 15 * len(key_years)))
        grand_row = f"{'Grand Total':<12}"
        for year in key_years:
            if year in count_pivot.columns:
                total_count = int(count_pivot[year].sum())
                total_spend = spend_pivot[year].sum()
                grand_row += f" | {total_count}/${total_spend:,.0f}"
            else:
                grand_row += f" | 0/$0"
        print(grand_row)
        
        # Save to Excel
        from constants.file_constants import ensure_output_directory
        ensure_output_directory()
        
        # Create combined summary with separate count and cost columns
        combined_data = []
        years = count_pivot.columns
        
        for lob in count_pivot.index:
            row_data = {'LOB': lob}
            for year in years:
                count = int(count_pivot.loc[lob, year])
                spend = spend_pivot.loc[lob, year]
                row_data[f'{year} Radio Count'] = count
                row_data[f'{year} Radio Spend'] = spend
            combined_data.append(row_data)
        
        combined_pivot = pd.DataFrame(combined_data)
        
        # Add Grand Total row
        grand_total_row = {'LOB': 'Grand Total'}
        for year in years:
            total_count = count_pivot[year].sum()
            total_spend = spend_pivot[year].sum()
            grand_total_row[f'{year} Radio Count'] = int(total_count)
            grand_total_row[f'{year} Radio Spend'] = total_spend
        
        # Add grand total as the last row
        combined_pivot = pd.concat([combined_pivot, pd.DataFrame([grand_total_row])], ignore_index=True)
        
        radio_output_path = get_output_file("RADIO_EQUIPMENT_COST_ANALYSIS")
        with pd.ExcelWriter(radio_output_path) as writer:
            combined_pivot.to_excel(writer, sheet_name=get_sheet_name('COMBINED_SUMMARY'))
            count_pivot.to_excel(writer, sheet_name=get_sheet_name('RADIO_COUNTS'))
            spend_pivot.to_excel(writer, sheet_name=get_sheet_name('RADIO_SPENDS'))
            df_pivot.to_excel(writer, sheet_name=get_sheet_name('RAW_DATA'), index=False)
        
        print(f"\nRadio Installation analysis saved to: {radio_output_path}")
        
        # Focus on ELEC OPERATIONS as requested
        if 'ELEC OPERATIONS' in radio_results:
            print(f"\n=== ELEC OPERATIONS Summary ===")
            elec_data = radio_results['ELEC OPERATIONS']
            total_count = sum(elec_data['counts'].values())
            total_spend = sum(elec_data['spends'].values())
            print(f"Total Radio Count (2026-2035): {total_count}")
            print(f"Total Radio Spend (2026-2035): ${total_spend:,.2f}")
            
            return count_pivot, spend_pivot
    
    return None, None

def analyze_vehicle_replacement_by_lob_vehicle_class_and_object_type():
    """Analyze Vehicle Replacement by LOB, Vehicle Class (L.H.P), and ObjectType - detailed hierarchical structure"""
    
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    print("=== Detailed Vehicle Replacement Analysis by LOB, Vehicle Class, and ObjectType ===\n")
    
    # Get unique LOB values (excluding invalid ones)
    lob_values = df_data['LOB from Location'].value_counts()
    valid_lobs = [lob for lob in lob_values.index if not pd.isna(lob) and lob != '#REF!']
    
    vehicle_classes = ['H', 'L', 'P']
    years = range(2026, 2036)
    
    # Initialize results dictionary with detailed hierarchical structure
    # Structure: {LOB: {vehicle_class: {object_type: {'counts': {year: count}, 'costs': {year: cost}}}}}
    detailed_vehicle_results = {}
    
    # Analyze each LOB
    for lob in valid_lobs:
        print(f"\n=== Analysis for {lob} ===")
        lob_data = df_data[df_data['LOB from Location'] == lob]
        print(f"Total {lob} records: {len(lob_data)}")
        
        detailed_vehicle_results[lob] = {}
        
        # Within each LOB, analyze by vehicle class
        for vehicle_class in vehicle_classes:
            print(f"\n  --- {lob} - Vehicle Class {vehicle_class} ---")
            
            # Filter for both LOB and vehicle class
            class_data = lob_data[lob_data['L.H.P'] == vehicle_class]
            print(f"  {lob} {vehicle_class} vehicles: {len(class_data)} records")
            
            if len(class_data) == 0:
                print(f"  No {vehicle_class} vehicles in {lob}")
                continue
            
            detailed_vehicle_results[lob][vehicle_class] = {}
            
            # Get unique ObjectTypes for this LOB and vehicle class combination
            object_types = class_data['ObjectType'].value_counts()
            valid_object_types = [obj_type for obj_type in object_types.index if not pd.isna(obj_type)]
            
            print(f"    ObjectTypes in {lob} {vehicle_class}: {', '.join(valid_object_types)}")
            
            # Within each vehicle class, analyze by ObjectType
            for object_type in valid_object_types:
                print(f"\n    --- {lob} - {vehicle_class} - {object_type} ---")
                
                # Filter for LOB, vehicle class, and object type
                object_data = class_data[class_data['ObjectType'] == object_type]
                print(f"    {lob} {vehicle_class} {object_type}: {len(object_data)} records")
                
                detailed_vehicle_results[lob][vehicle_class][object_type] = {'counts': {}, 'costs': {}}
                
                for year in years:
                    forecast_count_col = f'{year} Forecast Count'
                    replacement_cost_col = f'{year} Replacement Cost'
                    
                    if forecast_count_col not in df_data.columns or replacement_cost_col not in df_data.columns:
                        continue
                    
                    # Filter where Forecast Count = 1 (vehicles to be replaced)
                    forecast_filter = object_data[forecast_count_col] == 1
                    filtered_data = object_data[forecast_filter]
                    
                    # Count of records where Forecast Count = 1
                    vehicle_count = len(filtered_data)
                    
                    # Sum of Replacement Cost where Forecast Count = 1
                    replacement_cost = filtered_data[replacement_cost_col].fillna(0).sum()
                    
                    detailed_vehicle_results[lob][vehicle_class][object_type]['counts'][year] = vehicle_count
                    detailed_vehicle_results[lob][vehicle_class][object_type]['costs'][year] = replacement_cost
                    
                    if vehicle_count > 0 or replacement_cost > 0:
                        print(f"      {year}: Count={vehicle_count}, Cost=${replacement_cost:,.2f}")
    
    return detailed_vehicle_results


def analyze_vehicle_replacement_by_lhp_and_object_type():
    """Analyze Vehicle Replacement by L.H.P and ObjectType - across all LOBs"""
    
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    print("=== Vehicle Replacement Analysis by L.H.P and ObjectType ===\n")
    
    vehicle_classes = ['H', 'L', 'P']
    years = range(2025, 2036)  # Include 2025 as requested
    
    # Initialize results dictionary with L.H.P -> ObjectType structure
    # Structure: {vehicle_class: {object_type: {'counts': {year: count}, 'costs': {year: cost}}}}
    lhp_object_results = {}
    
    # Analyze each vehicle class
    for vehicle_class in vehicle_classes:
        print(f"\n=== Analysis for Vehicle Class {vehicle_class} ===")
        
        # Filter for this vehicle class across all LOBs
        class_data = df_data[df_data['L.H.P'] == vehicle_class]
        print(f"Total {vehicle_class} vehicles across all LOBs: {len(class_data)} records")
        
        if len(class_data) == 0:
            print(f"No {vehicle_class} vehicles found")
            continue
        
        lhp_object_results[vehicle_class] = {}
        
        # Get unique ObjectTypes for this vehicle class
        object_types = class_data['ObjectType'].value_counts()
        valid_object_types = [obj_type for obj_type in object_types.index if not pd.isna(obj_type)]
        
        print(f"ObjectTypes in {vehicle_class}: {', '.join(valid_object_types)}")
        
        # Within each vehicle class, analyze by ObjectType
        for object_type in valid_object_types:
            print(f"\n  --- {vehicle_class} - {object_type} ---")
            
            # Filter for vehicle class and object type (across all LOBs)
            object_data = class_data[class_data['ObjectType'] == object_type]
            print(f"  {vehicle_class} {object_type}: {len(object_data)} records")
            
            lhp_object_results[vehicle_class][object_type] = {'counts': {}, 'costs': {}}
            
            for year in years:
                forecast_count_col = f'{year} Forecast Count'
                replacement_cost_col = f'{year} Replacement Cost'
                
                if forecast_count_col not in df_data.columns:
                    continue
                
                # Filter where Forecast Count = 1 (vehicles to be replaced)
                forecast_filter = object_data[forecast_count_col] == 1
                filtered_data = object_data[forecast_filter]
                
                # Count of records where Forecast Count = 1
                vehicle_count = len(filtered_data)
                
                # Sum of Replacement Cost where Forecast Count = 1 (if column exists)
                replacement_cost = 0
                if replacement_cost_col in df_data.columns:
                    replacement_cost = filtered_data[replacement_cost_col].fillna(0).sum()
                
                lhp_object_results[vehicle_class][object_type]['counts'][year] = vehicle_count
                lhp_object_results[vehicle_class][object_type]['costs'][year] = replacement_cost
                
                if vehicle_count > 0:
                    if replacement_cost > 0:
                        print(f"    {year}: Count={vehicle_count}, Cost=${replacement_cost:,.2f}")
                    else:
                        print(f"    {year}: Count={vehicle_count}")
    
    return lhp_object_results


def analyze_vehicle_replacement_by_object_type_only():
    """Analyze Vehicle Replacement by ObjectType only - across all LOBs and L.H.P categories"""
    
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    print("=== Vehicle Replacement Analysis by ObjectType Only ===\n")
    
    years = range(2026, 2036)  # 2026-2035 as requested
    
    # Initialize results dictionary with ObjectType -> {year: {count, cost}} structure
    object_type_results = {}
    
    # Get all unique ObjectTypes across entire dataset
    unique_object_types = df_data['ObjectType'].value_counts()
    valid_object_types = [obj_type for obj_type in unique_object_types.index if not pd.isna(obj_type)]
    
    print(f"Total unique ObjectTypes found: {len(valid_object_types)}")
    print(f"ObjectTypes: {', '.join(sorted(valid_object_types))}")
    
    # Analyze each ObjectType across all LOBs and L.H.P categories
    for object_type in valid_object_types:
        print(f"\n--- ObjectType: {object_type} ---")
        
        # Filter for this ObjectType across all LOBs and L.H.P
        object_data = df_data[df_data['ObjectType'] == object_type]
        print(f"Total {object_type} records across all LOBs/L.H.P: {len(object_data)}")
        
        object_type_results[object_type] = {'counts': {}, 'costs': {}}
        
        for year in years:
            forecast_count_col = f'{year} Forecast Count'
            replacement_cost_col = f'{year} Replacement Cost'
            
            if forecast_count_col not in df_data.columns:
                continue
            
            # Filter where Forecast Count = 1 (vehicles to be replaced)
            forecast_filter = object_data[forecast_count_col] == 1
            filtered_data = object_data[forecast_filter]
            
            # Count of records where Forecast Count = 1
            vehicle_count = len(filtered_data)
            
            # Sum of Replacement Cost where Forecast Count = 1 (if column exists)
            replacement_cost = 0
            if replacement_cost_col in df_data.columns:
                replacement_cost = filtered_data[replacement_cost_col].fillna(0).sum()
            
            object_type_results[object_type]['counts'][year] = vehicle_count
            object_type_results[object_type]['costs'][year] = replacement_cost
            
            if vehicle_count > 0:
                if replacement_cost > 0:
                    print(f"  {year}: Count={vehicle_count}, Cost=${replacement_cost:,.2f}")
                else:
                    print(f"  {year}: Count={vehicle_count}")
    
    return object_type_results


def analyze_vehicle_replacement_by_lob_and_vehicle_class():
    """Analyze Vehicle Replacement by LOB and Vehicle Class (L.H.P) hierarchical structure"""
    
    # Read the data Excel file
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    print("=== Vehicle Replacement Analysis by LOB and Vehicle Class ===\n")
    
    # Get unique LOB values (excluding invalid ones)
    lob_values = df_data['LOB from Location'].value_counts()
    valid_lobs = [lob for lob in lob_values.index if not pd.isna(lob) and lob != '#REF!']
    
    vehicle_classes = ['H', 'L', 'P']
    years = range(2026, 2036)
    
    # Initialize results dictionary with hierarchical structure
    vehicle_results_hierarchical = {}
    
    # Analyze each LOB
    for lob in valid_lobs:
        print(f"\n=== Analysis for {lob} ===")
        lob_data = df_data[df_data['LOB from Location'] == lob]
        print(f"Total {lob} records: {len(lob_data)}")
        
        vehicle_results_hierarchical[lob] = {}
        
        # Within each LOB, analyze by vehicle class
        for vehicle_class in vehicle_classes:
            print(f"\n  --- {lob} - Vehicle Class {vehicle_class} ---")
            
            # Filter for both LOB and vehicle class
            class_data = lob_data[lob_data['L.H.P'] == vehicle_class]
            print(f"  {lob} {vehicle_class} vehicles: {len(class_data)} records")
            
            if len(class_data) == 0:
                print(f"  No {vehicle_class} vehicles in {lob}")
                continue
                
            vehicle_results_hierarchical[lob][vehicle_class] = {'counts': {}, 'costs': {}}
            
            for year in years:
                forecast_count_col = f'{year} Forecast Count'
                replacement_cost_col = f'{year} Replacement Cost'
                
                if forecast_count_col not in df_data.columns or replacement_cost_col not in df_data.columns:
                    continue
                
                # Filter where Forecast Count = 1 (vehicles to be replaced)
                forecast_filter = class_data[forecast_count_col] == 1
                filtered_data = class_data[forecast_filter]
                
                # Count of records where Forecast Count = 1
                vehicle_count = len(filtered_data)
                
                # Sum of Replacement Cost where Forecast Count = 1
                replacement_cost = filtered_data[replacement_cost_col].fillna(0).sum()
                
                vehicle_results_hierarchical[lob][vehicle_class]['counts'][year] = vehicle_count
                vehicle_results_hierarchical[lob][vehicle_class]['costs'][year] = replacement_cost
                
                if vehicle_count > 0 or replacement_cost > 0:
                    print(f"    {year}: Count={vehicle_count}, Cost=${replacement_cost:,.2f}")
    
    return vehicle_results_hierarchical

def create_detailed_vehicle_replacement_hierarchical_pivot_table():
    """Create detailed hierarchical pivot table for Vehicle Replacement analysis by LOB, Vehicle Class, and ObjectType"""
    
    # Get the detailed hierarchical vehicle replacement analysis results
    detailed_results = analyze_vehicle_replacement_by_lob_vehicle_class_and_object_type()
    
    print("\n=== Creating Detailed Hierarchical Vehicle Replacement Pivot Table ===")
    
    # Create detailed hierarchical structure for Excel
    combined_data = []
    years = range(2026, 2036)
    
    # Create the detailed hierarchical rows: LOB -> Vehicle Class -> ObjectType -> Vehicle Class Total -> LOB Total
    for lob in detailed_results.keys():
        print(f"Processing {lob}...")
        
        # Add LOB header row
        lob_header_row = {'LOB/Vehicle Class/ObjectType': lob}
        for year in years:
            lob_header_row[f'{year} Vehicle Count'] = 0  # LOB headers show 0
            lob_header_row[f'{year} Replacement Cost (Est.)'] = 0
        combined_data.append(lob_header_row)
        
        # Process each vehicle class within this LOB
        for vehicle_class in ['H', 'L', 'P']:
            if vehicle_class in detailed_results[lob]:
                # Add Vehicle Class header row
                vc_header_row = {'LOB/Vehicle Class/ObjectType': f'  {vehicle_class}'}  # Indented
                for year in years:
                    vc_header_row[f'{year} Vehicle Count'] = 0  # Vehicle class headers show 0
                    vc_header_row[f'{year} Replacement Cost (Est.)'] = 0
                combined_data.append(vc_header_row)
                
                # Add ObjectType rows under this vehicle class
                for object_type in detailed_results[lob][vehicle_class].keys():
                    obj_row = {'LOB/Vehicle Class/ObjectType': f'    {object_type}'}  # Double indented
                    
                    for year in years:
                        count = detailed_results[lob][vehicle_class][object_type]['counts'].get(year, 0)
                        cost = detailed_results[lob][vehicle_class][object_type]['costs'].get(year, 0)
                        obj_row[f'{year} Vehicle Count'] = count
                        obj_row[f'{year} Replacement Cost (Est.)'] = cost
                    
                    combined_data.append(obj_row)
                
                # Add Vehicle Class Total row
                vc_total_row = {'LOB/Vehicle Class/ObjectType': f'  {vehicle_class} Total'}  # Indented
                
                for year in years:
                    vc_total_count = 0
                    vc_total_cost = 0
                    
                    for object_type in detailed_results[lob][vehicle_class].keys():
                        vc_total_count += detailed_results[lob][vehicle_class][object_type]['counts'].get(year, 0)
                        vc_total_cost += detailed_results[lob][vehicle_class][object_type]['costs'].get(year, 0)
                    
                    vc_total_row[f'{year} Vehicle Count'] = vc_total_count
                    vc_total_row[f'{year} Replacement Cost (Est.)'] = vc_total_cost
                
                combined_data.append(vc_total_row)
        
        # Add LOB Total row
        lob_total_row = {'LOB/Vehicle Class/ObjectType': f'{lob} Total'}
        
        for year in years:
            lob_total_count = 0
            lob_total_cost = 0
            
            for vehicle_class in ['H', 'L', 'P']:
                if vehicle_class in detailed_results[lob]:
                    for object_type in detailed_results[lob][vehicle_class].keys():
                        lob_total_count += detailed_results[lob][vehicle_class][object_type]['counts'].get(year, 0)
                        lob_total_cost += detailed_results[lob][vehicle_class][object_type]['costs'].get(year, 0)
            
            lob_total_row[f'{year} Vehicle Count'] = lob_total_count
            lob_total_row[f'{year} Replacement Cost (Est.)'] = lob_total_cost
        
        combined_data.append(lob_total_row)
    
    # Add Grand Total row
    grand_total_row = {'LOB/Vehicle Class/ObjectType': 'Grand Total'}
    for year in years:
        grand_total_count = 0
        grand_total_cost = 0
        
        for lob in detailed_results.keys():
            for vehicle_class in ['H', 'L', 'P']:
                if vehicle_class in detailed_results[lob]:
                    for object_type in detailed_results[lob][vehicle_class].keys():
                        grand_total_count += detailed_results[lob][vehicle_class][object_type]['counts'].get(year, 0)
                        grand_total_cost += detailed_results[lob][vehicle_class][object_type]['costs'].get(year, 0)
        
        grand_total_row[f'{year} Vehicle Count'] = grand_total_count
        grand_total_row[f'{year} Replacement Cost (Est.)'] = grand_total_cost
    
    combined_data.append(grand_total_row)
    
    # Create DataFrame
    detailed_hierarchical_pivot = pd.DataFrame(combined_data)
    
    # Save to Excel
    ensure_database_directory()
    
    detailed_output_path = get_output_file("VEHICLE_REPLACEMENT_DETAILED_FORECAST")
    with pd.ExcelWriter(detailed_output_path) as writer:
        detailed_hierarchical_pivot.to_excel(writer, sheet_name=get_sheet_name('DETAILED_HIERARCHICAL_SUMMARY'), index=False)
    
    print(f"\nDetailed Hierarchical Vehicle Replacement analysis saved to: {detailed_output_path}")
    
    # Display sample of detailed hierarchical structure
    print("\n=== 2026 DETAILED HIERARCHICAL SUMMARY SAMPLE ===")
    print("LOB/Vehicle Class/ObjectType     | 2026 Vehicle Count | 2026 Replacement Cost (Est.)")
    print("-" * 90)
    
    # Show first few rows as sample
    for i, row in enumerate(combined_data[:20]):  # Show first 20 rows
        lob_vc_obj = row['LOB/Vehicle Class/ObjectType'][:30]  # Truncate long names
        count_2026 = row.get('2026 Vehicle Count', 0)
        cost_2026 = row.get('2026 Replacement Cost (Est.)', 0)
        print(f"{lob_vc_obj:<32} | {count_2026:>18} | ${cost_2026:>21,.0f}")
    
    print("... (showing first 20 rows)")
    print(f"\nTotal rows in detailed analysis: {len(combined_data)}")
    
    return detailed_hierarchical_pivot


def create_lhp_object_type_pivot_table():
    """Create pivot table for Vehicle Replacement analysis by L.H.P and ObjectType"""
    
    # Get the L.H.P and ObjectType analysis results
    lhp_results = analyze_vehicle_replacement_by_lhp_and_object_type()
    
    print("\n=== Creating L.H.P and ObjectType Pivot Table ===")
    
    # Create L.H.P -> ObjectType structure for Excel
    combined_data = []
    years = range(2025, 2036)  # Include 2025 as requested
    
    # Create the L.H.P -> ObjectType rows with totals
    for vehicle_class in ['H', 'L', 'P']:
        if vehicle_class in lhp_results:
            print(f"Processing Vehicle Class {vehicle_class}...")
            
            # Add Vehicle Class header row
            vc_header_row = {'L.H.P/ObjectType': vehicle_class}
            for year in years:
                vc_header_row[f'{year} Vehicle Count'] = 0  # Vehicle class headers show 0
                vc_header_row[f'{year} Replacement Cost (Est.)'] = 0
            combined_data.append(vc_header_row)
            
            # Add ObjectType rows under this vehicle class
            for object_type in lhp_results[vehicle_class].keys():
                obj_row = {'L.H.P/ObjectType': f'  {object_type}'}  # Indented
                
                for year in years:
                    count = lhp_results[vehicle_class][object_type]['counts'].get(year, 0)
                    cost = lhp_results[vehicle_class][object_type]['costs'].get(year, 0)
                    obj_row[f'{year} Vehicle Count'] = count
                    obj_row[f'{year} Replacement Cost (Est.)'] = cost
                
                combined_data.append(obj_row)
            
            # Add Vehicle Class Total row
            vc_total_row = {'L.H.P/ObjectType': f'{vehicle_class} Total'}
            
            for year in years:
                vc_total_count = 0
                vc_total_cost = 0
                
                for object_type in lhp_results[vehicle_class].keys():
                    vc_total_count += lhp_results[vehicle_class][object_type]['counts'].get(year, 0)
                    vc_total_cost += lhp_results[vehicle_class][object_type]['costs'].get(year, 0)
                
                vc_total_row[f'{year} Vehicle Count'] = vc_total_count
                vc_total_row[f'{year} Replacement Cost (Est.)'] = vc_total_cost
            
            combined_data.append(vc_total_row)
    
    # Add Grand Total row
    grand_total_row = {'L.H.P/ObjectType': 'Grand Total'}
    for year in years:
        grand_total_count = 0
        grand_total_cost = 0
        
        for vehicle_class in ['H', 'L', 'P']:
            if vehicle_class in lhp_results:
                for object_type in lhp_results[vehicle_class].keys():
                    grand_total_count += lhp_results[vehicle_class][object_type]['counts'].get(year, 0)
                    grand_total_cost += lhp_results[vehicle_class][object_type]['costs'].get(year, 0)
        
        grand_total_row[f'{year} Vehicle Count'] = grand_total_count
        grand_total_row[f'{year} Replacement Cost (Est.)'] = grand_total_cost
    
    combined_data.append(grand_total_row)
    
    # Create DataFrame
    lhp_object_pivot = pd.DataFrame(combined_data)
    
    # Save to Excel
    ensure_database_directory()
    
    lhp_output_path = get_output_file("VEHICLE_REPLACEMENT_BY_CATEGORY")
    with pd.ExcelWriter(lhp_output_path) as writer:
        lhp_object_pivot.to_excel(writer, sheet_name=get_sheet_name('LHP_OBJECTTYPE_SUMMARY'), index=False)
    
    print(f"\nL.H.P and ObjectType Vehicle Replacement analysis saved to: {lhp_output_path}")
    
    # Display sample of L.H.P -> ObjectType structure
    print("\n=== 2025-2026 L.H.P OBJECTTYPE SUMMARY SAMPLE ===")
    print("L.H.P/ObjectType          | 2025 Count | 2025 Cost      | 2026 Count | 2026 Cost")
    print("-" * 85)
    
    # Show first few rows as sample
    for i, row in enumerate(combined_data[:20]):  # Show first 20 rows
        lhp_obj = row['L.H.P/ObjectType'][:25]  # Truncate long names
        count_2025 = row.get('2025 Vehicle Count', 0)
        cost_2025 = row.get('2025 Replacement Cost (Est.)', 0)
        count_2026 = row.get('2026 Vehicle Count', 0)
        cost_2026 = row.get('2026 Replacement Cost (Est.)', 0)
        print(f"{lhp_obj:<25} | {count_2025:>10} | ${cost_2025:>12,.0f} | {count_2026:>10} | ${cost_2026:>10,.0f}")
    
    print("... (showing first 20 rows)")
    print(f"\nTotal rows in L.H.P/ObjectType analysis: {len(combined_data)}")
    print("✅ Now includes both Vehicle Count AND Replacement Cost (Est.) for each year!")
    
    return lhp_object_pivot


def create_freightliner_analysis_data():
    """Create Freightliner EV analysis data and return the DataFrame"""
    
    print("\n" + "="*60)
    print("=== Creating Freightliner EV Analysis Data ===")
    
    # EV RATIO CONSTANTS - Change these values in one place
    FREIGHTLINER_EV_RATIO_TOTAL = 7  # 6 ICE : 1 EV = 7 total vehicles
    
    # CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST = 125000  # $125,000 per ICE vehicle
    EV_CHASSIS_COST = 300000   # $300,000 per EV vehicle
    
    # Read data to calculate H vehicle counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate H vehicle counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"H vehicle calculations for all years:")
    for year in years:
        # Get count of H vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            h_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & (df_data['L.H.P'] == 'H')])
            
            # Apply 6:1 EV ratio calculation (6 ICE : 1 EV out of 7 total)
            # H - $ TOTAL 100% Freightliner ICE Vehicle = H vehicles - (H vehicles / RATIO_TOTAL)
            ice_vehicles_actual = h_vehicles_year - (h_vehicles_year / FREIGHTLINER_EV_RATIO_TOTAL)  # Unrounded for calculations
            ev_vehicles_from_total = h_vehicles_year / FREIGHTLINER_EV_RATIO_TOTAL  # EV vehicles from total
            
            # H - EV's needed based on 6 to 1 ratio = ICE vehicles / RATIO_TOTAL (using unrounded ICE value)
            ev_vehicles_needed_actual = ice_vehicles_actual / FREIGHTLINER_EV_RATIO_TOTAL  # Using actual unrounded ICE value
            
            # H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio = ICE - EV needed
            ice_less_ev_actual = ice_vehicles_actual - ev_vehicles_needed_actual  # Using unrounded values
            
            # Round for display
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_less_ev_rounded = int(round(ice_less_ev_actual))
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST * ice_vehicles_actual  # C4 = C3 * B4 (using unrounded)
            ev_needed_cost_actual = EV_CHASSIS_COST * ev_vehicles_needed_actual  # C7 = C6 * B7 (using unrounded)
            ice_less_ev_cost_actual = ICE_CHASSIS_COST * ice_less_ev_actual  # C9 = C3 * B9 (using unrounded)
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'h_vehicles_total': h_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_less_ev_actual,
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: H vehicles={h_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'h_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Freightliner analysis rows
    freightliner_data = []
    
    # Define the structure based on user requirements
    freightliner_rows = [
        'Freightliner',
        'H - 100% Freightliner ICE Vehicle per Budget',
        'H - $ TOTAL 100% Freightliner ICE Vehicle',
        '',  # Empty row for spacing
        'H - Avg Unit FRT EV Chassis',
        'H - EV\'s needed based on 6 to 1 ratio',
        '',  # Empty row for spacing
        'H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 6-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        '**** What is left from the 145 Heavy vehicles to 139 Freightliners Needed are Ford Super Duties with no EV Variant (6 SuperDuties).'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(freightliner_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # H - 100% Freightliner ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # H - $ TOTAL 100% Freightliner ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['ice_vehicles_rounded']  # ICE vehicles
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'H vehicles ({ref_data["h_vehicles_total"]}) less 6-1 EV ratio = {ref_data["ice_vehicles_actual"]:.2f}'
        elif i == 4:  # H - Avg Unit FRT EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST  # Use variable
            row_data['Notes'] = 'Per EV unit calculation'
        elif i == 5:  # H - EV's needed based on 6 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'ICE vehicles ({ref_data["ice_vehicles_actual"]:.2f}) / {FREIGHTLINER_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'ICE vehicles ({ref_data["ice_vehicles_actual"]:.2f}) - EV needed ({ref_data["ev_vehicles_needed_actual"]:.2f})'
        elif i == 9:  # Budget Total of 6-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE less EV (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # H - 100% Freightliner ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST  # Cost per unit
            elif i == 2:  # H - $ TOTAL 100% Freightliner ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['ice_vehicles_rounded']  # ICE vehicles count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # H - Avg Unit FRT EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST  # Cost per EV unit
            elif i == 5:  # H - EV's needed based on 6 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 6-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        freightliner_data.append(row_data)
    
    return freightliner_data


def create_freightliner_analysis():
    """Create dedicated Freightliner EV analysis with detailed vehicle scenarios"""
    
    print("\n" + "="*60)
    print("=== Creating Freightliner EV Analysis ===")
    
    # CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST = 125000  # $125,000 per ICE vehicle
    EV_CHASSIS_COST = 300000   # $300,000 per EV vehicle
    
    # Read data to calculate H vehicle count
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate H vehicle counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"H vehicle calculations for all years:")
    for year in years:
        # Get count of H vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            h_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & (df_data['L.H.P'] == 'H')])
            
            # Apply 6:1 EV ratio calculation (6 ICE : 1 EV out of 7 total)
            ev_vehicles_from_total = h_vehicles_year / 7  # EV vehicles from total count
            ice_vehicles_actual = h_vehicles_year - ev_vehicles_from_total  # Actual ICE vehicles (unrounded)
            ice_vehicles_rounded = int(round(ice_vehicles_actual))  # Rounded for display
            
            # Calculate EV's needed based on 6:1 ratio: (Total - Total/7) / 7
            ev_vehicles_needed_actual = ice_vehicles_actual / 7  # Actual EV vehicles needed (unrounded)
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))  # Rounded for display
            
            # Calculate ICE vehicles less EV vehicles needed
            ice_less_ev_actual = ice_vehicles_actual - ev_vehicles_needed_actual  # Actual value (unrounded)
            ice_less_ev_rounded = int(round(ice_less_ev_actual))  # Rounded for display
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST * ice_vehicles_actual  # Original ICE total cost
            ev_needed_cost_actual = EV_CHASSIS_COST * ev_vehicles_needed_actual  # EV vehicles needed cost  
            ice_less_ev_cost_actual = ICE_CHASSIS_COST * ice_less_ev_actual  # ICE less EV purchase cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'h_vehicles_total': h_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_less_ev_actual,
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: H vehicles={h_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'h_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Freightliner analysis rows
    freightliner_data = []
    
    # Define the structure based on user requirements
    freightliner_rows = [
        'Freightliner',
        'H - 100% Freightliner ICE Vehicle per Budget',
        'H - $ TOTAL 100% Freightliner ICE Vehicle',
        '',  # Empty row for spacing
        'H - Avg Unit FRT EV Chassis',
        'H - EV\'s needed based on 6 to 1 ratio',
        '',  # Empty row for spacing
        'H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 6-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        '**** What is left from the 145 Heavy vehicles to 139 Freightliners Needed are Ford Super Duties with no EV Variant (6 SuperDuties).'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(freightliner_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # H - 100% Freightliner ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # H - $ TOTAL 100% Freightliner ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['ice_vehicles_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total H vehicles ({ref_data["h_vehicles_total"]}) minus EV portion (6:1 ratio)'
        elif i == 4:  # H - Avg Unit FRT EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST  # Use variable
            row_data['Notes'] = 'Per EV unit calculation'
        elif i == 5:  # H - EV's needed based on 6 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'ICE vehicles ({ref_data["ice_vehicles_actual"]:.4f}) divided by 7'
        elif i == 7:  # H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'ICE vehicles minus EV needed ({ref_data["ice_vehicles_actual"]:.4f} - {ref_data["ev_vehicles_needed_actual"]:.4f})'
        elif i == 9:  # Budget Total of 6-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE less EV (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type (round for Excel display)
            if i == 1:  # H - 100% Freightliner ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST  # Cost per unit
            elif i == 2:  # H - $ TOTAL 100% Freightliner ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['ice_vehicles_rounded']  # ICE vehicle count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # H - Avg Unit FRT EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST  # Cost per EV unit
            elif i == 5:  # H - EV's needed based on 6 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE less EV count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 6-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        freightliner_data.append(row_data)
    
    # Create DataFrame
    freightliner_df = pd.DataFrame(freightliner_data)
    
    # Create output directory if it doesn't exist
    ensure_database_directory()
    
    # Save the Freightliner analysis to Excel
    output_path = get_output_file("HEAVY_VEHICLE_EV_TRANSITION_ANALYSIS")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Save main analysis
        freightliner_df.to_excel(writer, sheet_name=get_sheet_name('FREIGHTLINER_ANALYSIS'), index=False)
    
    print(f"\nFreightliner EV Analysis saved to: {output_path}")
    print(f"Sheet created: {get_sheet_name('FREIGHTLINER_ANALYSIS')}")
    print("✅ Dedicated Freightliner analysis with detailed EV scenarios:")
    print("  - Freightliner baseline analysis")
    print("  - 100% ICE Vehicle budget calculations")
    print("  - EV Chassis cost analysis")
    print("  - 6-to-1 EV ratio scenarios")
    print("  - Budget impact calculations")
    print("  - Ford Super Duties note (6 vehicles with no EV variant)")
    print(f"✅ Chassis cost variables:")
    print(f"  - ICE_CHASSIS_COST: ${ICE_CHASSIS_COST:,}")
    print(f"  - EV_CHASSIS_COST: ${EV_CHASSIS_COST:,}")
    print(f"✅ Sample calculations for {ref_year} (using actual unrounded numbers):")
    print(f"  - H - 100% Freightliner ICE Vehicle per Budget: 1 unit @ ${ICE_CHASSIS_COST:,}")
    print(f"  - H - $ TOTAL 100% Freightliner ICE Vehicle: {ref_data['ice_vehicles_rounded']} units @ ${ref_data['ice_total_cost_actual']:,.0f}")
    print(f"  - H - Avg Unit FRT EV Chassis: 1 unit @ ${EV_CHASSIS_COST:,}")
    print(f"  - H - EV's needed based on 6 to 1 ratio: {ref_data['ev_vehicles_needed_rounded']} units @ ${ref_data['ev_needed_cost_actual']:,.0f}")
    print(f"  - H - 100% Freightliner ICE Vehicles less 6-1 EV Vehicle Purchase Ratio: {ref_data['ice_less_ev_rounded']} units @ ${ref_data['ice_less_ev_cost_actual']:,.0f}")
    print(f"✅ New calculations for {ref_year}:")
    print(f"  - Budget Total (C11 = C9 + C7): ${ref_data['budget_total_cost_actual']:,.0f}")
    print(f"  - EV Premium Impact (C12 = C11 - C4): ${ref_data['ev_premium_impact_actual']:,.0f}")
    print(f"✅ Multi-year analysis:")
    print(f"  - Calculated for all years: {min(years)}-{max(years)}")
    print(f"  - All yearly columns populated with vehicle counts and costs")
    print(f"  - C11 and C12 formulas applied for each year")
    print(f"✅ Display optimization:")
    print(f"  - Calculations use actual unrounded values for precision")
    print(f"  - Excel display values rounded to nearest dollar for clean presentation")
    
    # Display structure summary
    print(f"\n=== FREIGHTLINER ANALYSIS STRUCTURE ===")
    print("Row                                          | Type")
    print("-" * 80)
    
    for i, row_name in enumerate(freightliner_rows[:10]):  # Show first 10 rows
        row_type = "Header" if row_name and not row_name.startswith('H -') else "Analysis" if row_name.startswith('H -') else "Spacer" if row_name == '' else "Note"
        print(f"{row_name:<40} | {row_type}")
    
    if len(freightliner_rows) > 10:
        print("... (additional rows)")
    
    print(f"\nTotal rows in Freightliner analysis: {len(freightliner_rows)}")
    print("✅ Includes columns: Vehicle Class, 2026 Units, Avg. Chassis Cost, Notes, plus yearly data (2026-2035)")


def create_van_ev_analysis_data():
    """Create Van EV analysis data and return the DataFrame"""
    
    print("\n" + "="*60)
    print("=== Creating Light Van EV Analysis Data ===")
    
    # EV RATIO CONSTANTS - Change these values in one place
    LIGHT_EV_RATIO_TOTAL = 4  # 3 ICE : 1 EV = 4 total vehicles
    
    # VAN CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_VAN = 62000   # $62,000 per ICE Van
    EV_CHASSIS_COST_VAN = 55000    # $55,000 per EV Van (cheaper than ICE!)
    
    # Read data to calculate L Van counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Van counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Van calculations for all years:")
    for year in years:
        # Get count of L Van vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_van_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                            (df_data['L.H.P'] == 'L') & 
                                            (df_data['ObjectType'] == 'VAN')])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_van_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_van_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_VAN * l_van_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_VAN * ev_vehicles_needed_actual  # EV vehicles cost
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_VAN * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_van_vehicles_total': l_van_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Vans={l_van_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_van_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Van analysis rows
    van_data = []
    
    # Define the structure based on user requirements
    van_rows = [
        'VANS',
        'L - 100% Van ICE Vehicle per Budget',
        'L - $ TOTAL 100% VAN ICE Vehicle',
        '',  # Empty row for spacing
        'L - Avg Unit Van EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Includes only Regular Vans, no Cutaway Van, No Dual Rear Wheel (DRW)'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(van_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Van ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_VAN  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% VAN ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['l_van_vehicles_total']  # Total Van count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Van vehicles ({ref_data["l_van_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Van EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_VAN  # Use variable
            row_data['Notes'] = 'Per EV Van unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Van vehicles ({ref_data["l_van_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Van vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Van ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_VAN  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% VAN ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['l_van_vehicles_total']  # Total Van count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Van EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_VAN  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        van_data.append(row_data)
    
    return van_data


def create_van_ev_analysis():
    """Create dedicated Light Van EV analysis with detailed vehicle scenarios"""
    
    print("\n" + "="*60)
    print("=== Creating Light Van EV Analysis ===")
    
    # VAN CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_VAN = 62000   # $62,000 per ICE Van
    EV_CHASSIS_COST_VAN = 55000    # $55,000 per EV Van (cheaper than ICE!)
    
    # Read data to calculate L Van counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Van counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Van calculations for all years:")
    for year in years:
        # Get count of L Van vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_van_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                            (df_data['L.H.P'] == 'L') & 
                                            (df_data['ObjectType'] == 'VAN')])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_van_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_van_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_VAN * l_van_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_VAN * ev_vehicles_needed_actual  # EV vehicles cost
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_VAN * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_van_vehicles_total': l_van_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Vans={l_van_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_van_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Van analysis rows
    van_data = []
    
    # Define the structure based on user requirements
    van_rows = [
        'VANS',
        'L - 100% Van ICE Vehicle per Budget',
        'L - $ TOTAL 100% VAN ICE Vehicle',
        '',  # Empty row for spacing
        'L - Avg Unit Van EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Includes only Regular Vans, no Cutaway Van, No Dual Rear Wheel (DRW)'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(van_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Van ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_VAN  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% VAN ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['l_van_vehicles_total']  # Total Van count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Van vehicles ({ref_data["l_van_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Van EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_VAN  # Use variable
            row_data['Notes'] = 'Per EV Van unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Van vehicles ({ref_data["l_van_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Van vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Van ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_VAN  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% VAN ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['l_van_vehicles_total']  # Total Van count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Van EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_VAN  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        van_data.append(row_data)
    
    # Create DataFrame
    van_df = pd.DataFrame(van_data)
    
    # Ensure output directory exists
    ensure_database_directory()
    
    # Save to Excel
    output_path = get_output_file("LIGHT_VAN_EV_TRANSITION_ANALYSIS")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        van_df.to_excel(writer, sheet_name=get_sheet_name('VAN_ANALYSIS'), index=False)
    
    print(f"\nVan EV Analysis saved to: {output_path}")
    print(f"Sheet created: {get_sheet_name('VAN_ANALYSIS')}")
    print("✅ Dedicated Light Van analysis with detailed EV scenarios:")
    print("  - Van baseline analysis")
    print("  - 100% ICE Van budget calculations")
    print("  - EV Van cost analysis")
    print("  - 3-to-1 EV ratio scenarios")
    print("  - Budget impact calculations (EV Vans are cheaper!)")
    print("  - Regular Vans only (no Cutaway, no DRW)")
    print(f"✅ Van chassis cost variables:")
    print(f"  - ICE_CHASSIS_COST_VAN: ${ICE_CHASSIS_COST_VAN:,}")
    print(f"  - EV_CHASSIS_COST_VAN: ${EV_CHASSIS_COST_VAN:,} (cheaper than ICE!)")
    print(f"✅ Sample calculations for {ref_year} (using actual unrounded numbers):")
    print(f"  - L - 100% Van ICE Vehicle per Budget: 1 unit @ ${ICE_CHASSIS_COST_VAN:,}")
    print(f"  - L - $ TOTAL 100% VAN ICE Vehicle: {ref_data['l_van_vehicles_total']} units @ ${ref_data['ice_total_cost_actual']:,.0f}")
    print(f"  - L - Avg Unit Van EV Chassis: 1 unit @ ${EV_CHASSIS_COST_VAN:,}")
    print(f"  - L - EV's needed based on 3 to 1 ratio: {ref_data['ev_vehicles_needed_rounded']} units @ ${ref_data['ev_needed_cost_actual']:,.0f}")
    print(f"  - L - 100% Van ICE Vehicles less 3-1 EV Vehicle Purchase Ratio: {ref_data['ice_less_ev_rounded']} units @ ${ref_data['ice_less_ev_cost_actual']:,.0f}")
    print(f"✅ New calculations for {ref_year}:")
    print(f"  - Budget Total (C11 = C9 + C7): ${ref_data['budget_total_cost_actual']:,.0f}")
    print(f"  - EV Premium Impact (C12 = C11 - C4): ${ref_data['ev_premium_impact_actual']:,.0f} (SAVINGS!)")
    print(f"✅ Multi-year analysis:")
    print(f"  - Calculated for all years: {min(years)}-{max(years)}")
    print(f"  - All yearly columns populated with vehicle counts and costs")
    print(f"  - C11 and C12 formulas applied for each year")
    print(f"✅ Display optimization:")
    print(f"  - Calculations use actual unrounded values for precision")
    print(f"  - Excel display values rounded to nearest dollar for clean presentation")


def create_car_suv_ev_analysis_data():
    """Create Car/SUV EV analysis data and return the DataFrame"""
    
    print("\n" + "="*60)
    print("=== Creating Light Car/SUV EV Analysis Data ===")
    
    # EV RATIO CONSTANTS - Change these values in one place
    LIGHT_EV_RATIO_TOTAL = 4  # 3 ICE : 1 EV = 4 total vehicles
    
    # CAR/SUV CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_CAR = 43000   # $43,000 per ICE Car/SUV
    EV_CHASSIS_COST_CAR = 46000    # $46,000 per EV Car/SUV (more expensive than ICE)
    
    # Read data to calculate L Car/SUV counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Car/SUV counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Car/SUV calculations for all years:")
    for year in years:
        # Get count of L Car/SUV vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_car_suv_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                                (df_data['L.H.P'] == 'L') & 
                                                ((df_data['ObjectType'] == 'CAR') | (df_data['ObjectType'] == 'SPORT_UTIL'))])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_car_suv_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_car_suv_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_CAR * l_car_suv_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_CAR * ev_vehicles_needed_actual  # EV vehicles cost
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_CAR * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_car_suv_vehicles_total': l_car_suv_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Car/SUV={l_car_suv_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_car_suv_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Car/SUV analysis rows
    car_suv_data = []
    
    # Define the structure based on user requirements
    car_suv_rows = [
        'CAR',
        'L - 100% Car / SUV ICE Vehicle per Budget',
        'L - $ TOTAL 100% Car / SUV ICE Vehicle',
        '',  # Empty row for spacing
        'L - Avg Unit Car / SUV EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Includes Cars and Sport Utility Vehicles (SUVs)'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(car_suv_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Car / SUV ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_CAR  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% Car / SUV ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['l_car_suv_vehicles_total']  # Total Car/SUV count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Car/SUV vehicles ({ref_data["l_car_suv_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Car / SUV EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_CAR  # Use variable
            row_data['Notes'] = 'Per EV Car/SUV unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Car/SUV vehicles ({ref_data["l_car_suv_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Car/SUV vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Car / SUV ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_CAR  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% Car / SUV ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['l_car_suv_vehicles_total']  # Total Car/SUV count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Car / SUV EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_CAR  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        car_suv_data.append(row_data)
    
    return car_suv_data


def create_car_suv_ev_analysis():
    """Create dedicated Light Car/SUV EV analysis with detailed vehicle scenarios"""
    
    print("\n" + "="*60)
    print("=== Creating Light Car/SUV EV Analysis ===")
    
    # CAR/SUV CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_CAR = 43000   # $43,000 per ICE Car/SUV
    EV_CHASSIS_COST_CAR = 46000    # $46,000 per EV Car/SUV (more expensive than ICE)
    
    # Read data to calculate L Car/SUV counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Car/SUV counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Car/SUV calculations for all years:")
    for year in years:
        # Get count of L Car/SUV vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_car_suv_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                                (df_data['L.H.P'] == 'L') & 
                                                ((df_data['ObjectType'] == 'CAR') | (df_data['ObjectType'] == 'SPORT_UTIL'))])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_car_suv_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_car_suv_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_CAR * l_car_suv_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_CAR * ev_vehicles_needed_actual  # EV vehicles cost
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_CAR * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_car_suv_vehicles_total': l_car_suv_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Car/SUV={l_car_suv_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_car_suv_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Car/SUV analysis rows
    car_suv_data = []
    
    # Define the structure based on user requirements
    car_suv_rows = [
        'CAR',
        'L - 100% Car / SUV ICE Vehicle per Budget',
        'L - $ TOTAL 100% Car / SUV ICE Vehicle',
        '',  # Empty row for spacing
        'L - Avg Unit Car / SUV EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Includes Cars and Sport Utility Vehicles (SUVs)'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(car_suv_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Car / SUV ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_CAR  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% Car / SUV ICE Vehicle
            row_data['"2026\nUnits"'] = ref_data['l_car_suv_vehicles_total']  # Total Car/SUV count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Car/SUV vehicles ({ref_data["l_car_suv_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Car / SUV EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_CAR  # Use variable
            row_data['Notes'] = 'Per EV Car/SUV unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Car/SUV vehicles ({ref_data["l_car_suv_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Car/SUV vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Car / SUV ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_CAR  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% Car / SUV ICE Vehicle
                row_data[f'"{year}\nUnits"'] = year_data['l_car_suv_vehicles_total']  # Total Car/SUV count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Car / SUV EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_CAR  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        car_suv_data.append(row_data)
    
    # Create DataFrame
    car_suv_df = pd.DataFrame(car_suv_data)
    
    # Ensure output directory exists
    ensure_database_directory()
    
    # Save to Excel
    output_path = 'output/Car_SUV_EV_Analysis.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        car_suv_df.to_excel(writer, sheet_name='Car_SUV_Analysis', index=False)
    
    print(f"\nCar/SUV EV Analysis saved to: {output_path}")
    print("Sheet created: Car_SUV_Analysis")
    print("✅ Dedicated Light Car/SUV analysis with detailed EV scenarios:")
    print("  - Car/SUV baseline analysis")
    print("  - 100% ICE Car/SUV budget calculations")
    print("  - EV Car/SUV cost analysis")
    print("  - 3-to-1 EV ratio scenarios")
    print("  - Budget impact calculations (EV Cars/SUVs are more expensive)")
    print("  - Includes Cars and Sport Utility Vehicles (SUVs)")
    print(f"✅ Car/SUV chassis cost variables:")
    print(f"  - ICE_CHASSIS_COST_CAR: ${ICE_CHASSIS_COST_CAR:,}")
    print(f"  - EV_CHASSIS_COST_CAR: ${EV_CHASSIS_COST_CAR:,} (more expensive than ICE)")
    print(f"✅ Sample calculations for {ref_year} (using actual unrounded numbers):")
    print(f"  - L - 100% Car / SUV ICE Vehicle per Budget: 1 unit @ ${ICE_CHASSIS_COST_CAR:,}")
    print(f"  - L - $ TOTAL 100% Car / SUV ICE Vehicle: {ref_data['l_car_suv_vehicles_total']} units @ ${ref_data['ice_total_cost_actual']:,.0f}")
    print(f"  - L - Avg Unit Car / SUV EV Chassis: 1 unit @ ${EV_CHASSIS_COST_CAR:,}")
    print(f"  - L - EV's needed based on 3 to 1 ratio: {ref_data['ev_vehicles_needed_rounded']} units @ ${ref_data['ev_needed_cost_actual']:,.0f}")
    print(f"  - L - 100% Car / SUV ICE Vehicles less 3-1 EV Vehicle Purchase Ratio: {ref_data['ice_less_ev_rounded']} units @ ${ref_data['ice_less_ev_cost_actual']:,.0f}")
    print(f"✅ New calculations for {ref_year}:")
    print(f"  - Budget Total (C11 = C9 + C7): ${ref_data['budget_total_cost_actual']:,.0f}")
    print(f"  - EV Premium Impact (C12 = C11 - C4): ${ref_data['ev_premium_impact_actual']:,.0f} (PREMIUM COST)")
    print(f"✅ Multi-year analysis:")
    print(f"  - Calculated for all years: {min(years)}-{max(years)}")
    print(f"  - All yearly columns populated with vehicle counts and costs")
    print(f"  - C11 and C12 formulas applied for each year")
    print(f"✅ Display optimization:")
    print(f"  - Calculations use actual unrounded values for precision")
    print(f"  - Excel display values rounded to nearest dollar for clean presentation")


def create_pickup_ev_analysis_data():
    """Create Pickup EV analysis data and return the DataFrame"""
    
    print("\n" + "="*60)
    print("=== Creating Light Pickup EV Analysis Data ===")
    
    # EV RATIO CONSTANTS - Change these values in one place
    LIGHT_EV_RATIO_TOTAL = 4  # 3 ICE : 1 EV = 4 total vehicles
    
    # PICKUP CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_PICKUP = 44000   # $44,000 per ICE Pickup
    EV_CHASSIS_COST_PICKUP = 54000    # $54,000 per EV Pickup (more expensive than ICE)
    
    # Read data to calculate L Pickup counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Pickup counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Pickup calculations for all years:")
    for year in years:
        # Get count of L Pickup vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_pickup_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                               (df_data['L.H.P'] == 'L') & 
                                               (df_data['ObjectType'] == 'PICKUP')])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_pickup_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_pickup_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_PICKUP * l_pickup_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_PICKUP * ev_vehicles_needed_actual  # EV vehicles cost (using actual fractional amount)
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_PICKUP * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_pickup_vehicles_total': l_pickup_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Pickups={l_pickup_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_pickup_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Pickup analysis rows
    pickup_data = []
    
    # Define the structure based on user requirements
    pickup_rows = [
        'PICK UP',
        'L - 100% Pick Up ICE Vehicle per Budget',
        'L - $ TOTAL 100% Pick Up ICE Vehicle ****',
        '',  # Empty row for spacing
        'L - Avg Unit Pick Up EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Light Duty Pickup Trucks Only'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(pickup_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Pick Up ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_PICKUP  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% Pick Up ICE Vehicle ****
            row_data['"2026\nUnits"'] = ref_data['l_pickup_vehicles_total']  # Total Pickup count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Pickup vehicles ({ref_data["l_pickup_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Pick Up EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_PICKUP  # Use variable
            row_data['Notes'] = 'Per EV Pickup unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Pickup vehicles ({ref_data["l_pickup_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Pickup vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Pick Up ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_PICKUP  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% Pick Up ICE Vehicle ****
                row_data[f'"{year}\nUnits"'] = year_data['l_pickup_vehicles_total']  # Total Pickup count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Pick Up EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_PICKUP  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        pickup_data.append(row_data)
    
    return pickup_data


def create_pickup_ev_analysis():
    """Create dedicated Light Pickup EV analysis with detailed vehicle scenarios"""
    
    print("\n" + "="*60)
    print("=== Creating Light Pickup EV Analysis ===")
    
    # PICKUP CHASSIS COST VARIABLES - Change these values in one place
    ICE_CHASSIS_COST_PICKUP = 44000   # $44,000 per ICE Pickup
    EV_CHASSIS_COST_PICKUP = 54000    # $54,000 per EV Pickup (more expensive than ICE)
    
    # Read data to calculate L Pickup counts
    data_file = get_input_file_safe("VEHICLE_FLEET_MASTER_DATA")
    if data_file is None:
        print("No vehicle fleet master data found. Returning empty results.")
        return {}, {}
    df_data = pd.read_excel(data_file)
    
    # Define years for analysis
    years = list(range(2026, 2036))  # 2026-2035
    
    # Calculate L Pickup counts and EV ratios for all years
    yearly_calculations = {}
    
    print(f"L Pickup calculations for all years:")
    for year in years:
        # Get count of L Pickup vehicles where [Year] Forecast Count is 1
        forecast_col = f'{year} Forecast Count'
        if forecast_col in df_data.columns:
            l_pickup_vehicles_year = len(df_data[(df_data[forecast_col] == 1) & 
                                               (df_data['L.H.P'] == 'L') & 
                                               (df_data['ObjectType'] == 'PICKUP')])
            
            # Apply 3:1 EV ratio calculation (3 ICE : 1 EV out of 4 total)
            ev_vehicles_needed_actual = l_pickup_vehicles_year / LIGHT_EV_RATIO_TOTAL  # EV vehicles needed (1/4)
            ice_vehicles_actual = l_pickup_vehicles_year - ev_vehicles_needed_actual  # ICE vehicles (3/4)
            
            # Round for display
            ev_vehicles_needed_rounded = int(round(ev_vehicles_needed_actual))
            ice_vehicles_rounded = int(round(ice_vehicles_actual))
            ice_less_ev_rounded = ice_vehicles_rounded  # Same as ICE vehicles for 3:1 ratio
            
            # Calculate costs using variables
            ice_total_cost_actual = ICE_CHASSIS_COST_PICKUP * l_pickup_vehicles_year  # Original all-ICE cost
            ev_needed_cost_actual = EV_CHASSIS_COST_PICKUP * ev_vehicles_needed_actual  # EV vehicles cost (using actual fractional amount)
            ice_less_ev_cost_actual = ICE_CHASSIS_COST_PICKUP * ice_vehicles_actual  # Remaining ICE cost
            budget_total_cost_actual = ice_less_ev_cost_actual + ev_needed_cost_actual  # C11 = C9 + C7
            ev_premium_impact_actual = budget_total_cost_actual - ice_total_cost_actual  # C12 = C11 - C4
            
            # Store all calculations for this year
            yearly_calculations[year] = {
                'l_pickup_vehicles_total': l_pickup_vehicles_year,
                'ice_vehicles_actual': ice_vehicles_actual,
                'ice_vehicles_rounded': ice_vehicles_rounded,
                'ev_vehicles_needed_actual': ev_vehicles_needed_actual,
                'ev_vehicles_needed_rounded': ev_vehicles_needed_rounded,
                'ice_less_ev_actual': ice_vehicles_actual,  # Same as ICE for 3:1 ratio
                'ice_less_ev_rounded': ice_less_ev_rounded,
                'ice_total_cost_actual': ice_total_cost_actual,
                'ev_needed_cost_actual': ev_needed_cost_actual,
                'ice_less_ev_cost_actual': ice_less_ev_cost_actual,
                'budget_total_cost_actual': budget_total_cost_actual,
                'ev_premium_impact_actual': ev_premium_impact_actual
            }
            
            print(f"  {year}: L Pickups={l_pickup_vehicles_year}, ICE={ice_vehicles_rounded}, EV needed={ev_vehicles_needed_rounded}, ICE less EV={ice_less_ev_rounded}")
        else:
            print(f"  {year}: No forecast data available")
            # Set all values to 0 for missing years
            yearly_calculations[year] = {
                'l_pickup_vehicles_total': 0, 'ice_vehicles_actual': 0, 'ice_vehicles_rounded': 0,
                'ev_vehicles_needed_actual': 0, 'ev_vehicles_needed_rounded': 0,
                'ice_less_ev_actual': 0, 'ice_less_ev_rounded': 0,
                'ice_total_cost_actual': 0, 'ev_needed_cost_actual': 0,
                'ice_less_ev_cost_actual': 0, 'budget_total_cost_actual': 0,
                'ev_premium_impact_actual': 0
            }
    
    # Create the Pickup analysis rows
    pickup_data = []
    
    # Define the structure based on user requirements
    pickup_rows = [
        'PICK UP',
        'L - 100% Pick Up ICE Vehicle per Budget',
        'L - $ TOTAL 100% Pick Up ICE Vehicle ****',
        '',  # Empty row for spacing
        'L - Avg Unit Pick Up EV Chassis',
        'L - EV\'s needed based on 3 to 1 ratio',
        '',  # Empty row for spacing
        'L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio',
        '',  # Empty row for spacing
        'Budget Total of 3-1 Ratio Scenario EVs and ICE',
        'EV Premium Impact to Budget',
        '',  # Empty row for spacing
        'Light Duty Pickup Trucks Only'
    ]
    
    # Use 2026 data as reference for display in "2026 Units" and "Avg. Chassis Cost" columns
    ref_year = 2026
    ref_data = yearly_calculations[ref_year]
    
    # Build the data structure
    for i, row_name in enumerate(pickup_rows):
        row_data = {'Vehicle Class': row_name}
        
        # Set specific values based on row type (using 2026 as reference year)
        if i == 1:  # L - 100% Pick Up ICE Vehicle per Budget
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = ICE_CHASSIS_COST_PICKUP  # Use variable
            row_data['Notes'] = 'Per unit calculation'
        elif i == 2:  # L - $ TOTAL 100% Pick Up ICE Vehicle ****
            row_data['"2026\nUnits"'] = ref_data['l_pickup_vehicles_total']  # Total Pickup count
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total L Pickup vehicles ({ref_data["l_pickup_vehicles_total"]}) all ICE cost'
        elif i == 4:  # L - Avg Unit Pick Up EV Chassis
            row_data['"2026\nUnits"'] = 1  # 1 unit for calculation
            row_data['Avg. Chassis Cost'] = EV_CHASSIS_COST_PICKUP  # Use variable
            row_data['Notes'] = 'Per EV Pickup unit calculation'
        elif i == 5:  # L - EV's needed based on 3 to 1 ratio
            row_data['"2026\nUnits"'] = ref_data['ev_vehicles_needed_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_needed_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Pickup vehicles ({ref_data["l_pickup_vehicles_total"]}) / {LIGHT_EV_RATIO_TOTAL} = {ref_data["ev_vehicles_needed_actual"]:.2f}'
        elif i == 7:  # L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
            row_data['"2026\nUnits"'] = ref_data['ice_less_ev_rounded']  # Rounded for display
            row_data['Avg. Chassis Cost'] = round(ref_data['ice_less_ev_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'L Pickup vehicles remaining as ICE after 3:1 ratio ({ref_data["ice_vehicles_actual"]:.2f})'
        elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
            row_data['"2026\nUnits"'] = 0  # No units for total row
            row_data['Avg. Chassis Cost'] = round(ref_data['budget_total_cost_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Total budget: ICE remaining (${ref_data["ice_less_ev_cost_actual"]:,.0f}) + EV needed (${ref_data["ev_needed_cost_actual"]:,.0f})'
        elif i == 10:  # EV Premium Impact to Budget
            row_data['"2026\nUnits"'] = 0  # No units for impact row
            row_data['Avg. Chassis Cost'] = round(ref_data['ev_premium_impact_actual'], 0)  # Round for Excel display
            row_data['Notes'] = f'Budget impact: Total (${ref_data["budget_total_cost_actual"]:,.0f}) - Original ICE (${ref_data["ice_total_cost_actual"]:,.0f})'
        else:
            row_data['"2026\nUnits"'] = 0  # Placeholder for other rows
            row_data['Avg. Chassis Cost'] = 0
            row_data['Notes'] = ''
        
        # Add yearly columns with calculated values (round for Excel display)
        for year in years:
            year_data = yearly_calculations[year]
            
            # Set vehicle counts and costs based on row type
            if i == 1:  # L - 100% Pick Up ICE Vehicle per Budget
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = ICE_CHASSIS_COST_PICKUP  # Cost per unit
            elif i == 2:  # L - $ TOTAL 100% Pick Up ICE Vehicle ****
                row_data[f'"{year}\nUnits"'] = year_data['l_pickup_vehicles_total']  # Total Pickup count
                row_data[f'{year}'] = round(year_data['ice_total_cost_actual'], 0)  # Round for Excel
            elif i == 4:  # L - Avg Unit Pick Up EV Chassis
                row_data[f'"{year}\nUnits"'] = 1  # Always 1 unit
                row_data[f'{year}'] = EV_CHASSIS_COST_PICKUP  # Cost per EV unit
            elif i == 5:  # L - EV's needed based on 3 to 1 ratio
                row_data[f'"{year}\nUnits"'] = year_data['ev_vehicles_needed_rounded']  # EV count needed
                row_data[f'{year}'] = round(year_data['ev_needed_cost_actual'], 0)  # Round for Excel
            elif i == 7:  # L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio
                row_data[f'"{year}\nUnits"'] = year_data['ice_less_ev_rounded']  # ICE remaining count
                row_data[f'{year}'] = round(year_data['ice_less_ev_cost_actual'], 0)  # Round for Excel
            elif i == 9:  # Budget Total of 3-1 Ratio Scenario EVs and ICE
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for total row
                row_data[f'{year}'] = round(year_data['budget_total_cost_actual'], 0)  # Round for Excel
            elif i == 10:  # EV Premium Impact to Budget
                row_data[f'"{year}\nUnits"'] = 0  # No vehicle count for impact row
                row_data[f'{year}'] = round(year_data['ev_premium_impact_actual'], 0)  # Round for Excel
            else:
                row_data[f'"{year}\nUnits"'] = 0  # Placeholder for other rows
                row_data[f'{year}'] = 0
        
        pickup_data.append(row_data)
    
    # Create DataFrame
    pickup_df = pd.DataFrame(pickup_data)
    
    # Ensure output directory exists
    ensure_database_directory()
    
    # Save to Excel
    output_path = 'output/Pickup_EV_Analysis.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        pickup_df.to_excel(writer, sheet_name='Pickup_Analysis', index=False)
    
    print(f"\nPickup EV Analysis saved to: {output_path}")
    print("Sheet created: Pickup_Analysis")
    print("✅ Dedicated Light Pickup analysis with detailed EV scenarios:")
    print("  - Pickup baseline analysis")
    print("  - 100% ICE Pickup budget calculations")
    print("  - EV Pickup cost analysis")
    print("  - 3-to-1 EV ratio scenarios")
    print("  - Budget impact calculations (EV Pickups are more expensive)")
    print("  - Light Duty Pickup Trucks Only")
    print(f"✅ Pickup chassis cost variables:")
    print(f"  - ICE_CHASSIS_COST_PICKUP: ${ICE_CHASSIS_COST_PICKUP:,}")
    print(f"  - EV_CHASSIS_COST_PICKUP: ${EV_CHASSIS_COST_PICKUP:,} (more expensive than ICE)")
    print(f"✅ Sample calculations for {ref_year} (using actual unrounded numbers):")
    print(f"  - L - 100% Pick Up ICE Vehicle per Budget: 1 unit @ ${ICE_CHASSIS_COST_PICKUP:,}")
    print(f"  - L - $ TOTAL 100% Pick Up ICE Vehicle: {ref_data['l_pickup_vehicles_total']} units @ ${ref_data['ice_total_cost_actual']:,.0f}")
    print(f"  - L - Avg Unit Pick Up EV Chassis: 1 unit @ ${EV_CHASSIS_COST_PICKUP:,}")
    print(f"  - L - EV's needed based on 3 to 1 ratio: {ref_data['ev_vehicles_needed_rounded']} units @ ${ref_data['ev_needed_cost_actual']:,.0f}")
    print(f"  - L - 100% Pick Up ICE Vehicles less 3-1 EV Vehicle Purchase Ratio: {ref_data['ice_less_ev_rounded']} units @ ${ref_data['ice_less_ev_cost_actual']:,.0f}")
    print(f"✅ New calculations for {ref_year}:")
    print(f"  - Budget Total (C11 = C9 + C7): ${ref_data['budget_total_cost_actual']:,.0f}")
    print(f"  - EV Premium Impact (C12 = C11 - C4): ${ref_data['ev_premium_impact_actual']:,.0f} (PREMIUM COST)")
    print(f"✅ Multi-year analysis:")
    print(f"  - Calculated for all years: {min(years)}-{max(years)}")
    print(f"  - All yearly columns populated with vehicle counts and costs")
    print(f"  - C11 and C12 formulas applied for each year")
    print(f"✅ Display optimization:")
    print(f"  - Calculations use actual unrounded values for precision")
    print(f"  - Excel display values rounded to nearest dollar for clean presentation")


def create_object_type_only_pivot_table():
    """Create pivot table for Vehicle Replacement analysis by ObjectType only"""
    
    # Get the ObjectType-only analysis results
    object_type_results = analyze_vehicle_replacement_by_object_type_only()
    
    print("\n=== Creating ObjectType-Only Pivot Table ===")
    
    # Create ObjectType structure for Excel
    combined_data = []
    years = range(2026, 2036)  # 2026-2035 as requested
    
    # Sort ObjectTypes alphabetically for consistent ordering
    sorted_object_types = sorted(object_type_results.keys())
    
    # Create ObjectType rows
    for object_type in sorted_object_types:
        print(f"Processing ObjectType: {object_type}...")
        
        obj_row = {'ObjectType': object_type}
        
        for year in years:
            count = object_type_results[object_type]['counts'].get(year, 0)
            cost = object_type_results[object_type]['costs'].get(year, 0)
            obj_row[f'{year} Vehicle Count'] = count
            obj_row[f'{year} Replacement Cost (Est.)'] = cost
        
        combined_data.append(obj_row)
    
    # Add Grand Total row
    grand_total_row = {'ObjectType': 'Grand Total'}
    for year in years:
        grand_total_count = 0
        grand_total_cost = 0
        
        for object_type in object_type_results.keys():
            grand_total_count += object_type_results[object_type]['counts'].get(year, 0)
            grand_total_cost += object_type_results[object_type]['costs'].get(year, 0)
        
        grand_total_row[f'{year} Vehicle Count'] = grand_total_count
        grand_total_row[f'{year} Replacement Cost (Est.)'] = grand_total_cost
    
    combined_data.append(grand_total_row)
    
    # Create DataFrame
    object_type_pivot = pd.DataFrame(combined_data)
    
    # Save to Excel
    ensure_database_directory()
    
    with pd.ExcelWriter('output/Vehicle_Replacement_ObjectType_Only.xlsx') as writer:
        object_type_pivot.to_excel(writer, sheet_name='ObjectType_Summary', index=False)
    
    print(f"\nObjectType-Only Vehicle Replacement analysis saved to: output/Vehicle_Replacement_ObjectType_Only.xlsx")
    
    # Display sample of ObjectType structure
    print("\n=== 2026 OBJECTTYPE SUMMARY SAMPLE ===")
    print("ObjectType            | 2026 Vehicle Count | 2026 Replacement Cost (Est.)")
    print("-" * 75)
    
    # Show first few rows as sample
    for i, row in enumerate(combined_data[:15]):  # Show first 15 rows
        obj_type = row['ObjectType'][:18]  # Truncate long names
        count_2026 = row.get('2026 Vehicle Count', 0)
        cost_2026 = row.get('2026 Replacement Cost (Est.)', 0)
        print(f"{obj_type:<18} | {count_2026:>18} | ${cost_2026:>21,.0f}")
    
    print("... (showing first 15 rows)")
    print(f"\nTotal ObjectTypes in analysis: {len(combined_data)-1}")  # -1 for Grand Total
    print("✅ Pure ObjectType analysis across all LOBs and L.H.P categories!")
    print("✅ Includes both Vehicle Count AND Replacement Cost for each year!")
    
    return object_type_pivot


def create_vehicle_replacement_hierarchical_pivot_table():
    """Create hierarchical pivot table for Vehicle Replacement analysis by LOB and Vehicle Class"""
    
    # Get the hierarchical vehicle replacement analysis results
    vehicle_results = analyze_vehicle_replacement_by_lob_and_vehicle_class()
    
    print("\n=== Creating Hierarchical Vehicle Replacement Pivot Table ===")
    
    # Create hierarchical structure for Excel
    combined_data = []
    years = range(2026, 2036)
    
    # Create the hierarchical rows: LOB, then H/L/P under each LOB
    for lob in vehicle_results.keys():
        # Add LOB header row (totals for this LOB)
        lob_row = {'LOB/Vehicle Class': lob}
        
        # Calculate LOB totals across all vehicle classes
        for year in years:
            lob_total_count = 0
            lob_total_spend = 0
            
            for vehicle_class in ['H', 'L', 'P']:
                if vehicle_class in vehicle_results[lob]:
                    lob_total_count += vehicle_results[lob][vehicle_class]['counts'].get(year, 0)
                    lob_total_spend += vehicle_results[lob][vehicle_class]['costs'].get(year, 0)
            
            lob_row[f'{year} Vehicle Count'] = lob_total_count
            lob_row[f'{year} Replacement Cost (Est.)'] = lob_total_spend
        
        combined_data.append(lob_row)
        
        # Add vehicle class rows under this LOB
        for vehicle_class in ['H', 'L', 'P']:
            if vehicle_class in vehicle_results[lob]:
                vc_row = {'LOB/Vehicle Class': f'  {vehicle_class}'}  # Indented to show hierarchy
                
                for year in years:
                    count = vehicle_results[lob][vehicle_class]['counts'].get(year, 0)
                    spend = vehicle_results[lob][vehicle_class]['costs'].get(year, 0)
                    vc_row[f'{year} Vehicle Count'] = count
                    vc_row[f'{year} Replacement Cost (Est.)'] = spend
                
                combined_data.append(vc_row)
    
    # Add Grand Total row
    grand_total_row = {'LOB/Vehicle Class': 'Grand Total'}
    for year in years:
        total_count = 0
        total_spend = 0
        
        for lob in vehicle_results.keys():
            for vehicle_class in ['H', 'L', 'P']:
                if vehicle_class in vehicle_results[lob]:
                    total_count += vehicle_results[lob][vehicle_class]['counts'].get(year, 0)
                    total_spend += vehicle_results[lob][vehicle_class]['costs'].get(year, 0)
        
        grand_total_row[f'{year} Vehicle Count'] = total_count
        grand_total_row[f'{year} Replacement Cost (Est.)'] = total_spend
    
    combined_data.append(grand_total_row)
    
    # Create DataFrame
    hierarchical_pivot = pd.DataFrame(combined_data)
    
    # Save to Excel
    ensure_database_directory()
    
    with pd.ExcelWriter('output/Vehicle_Replacement_Hierarchical.xlsx') as writer:
        hierarchical_pivot.to_excel(writer, sheet_name='Hierarchical_Summary', index=False)
    
    print(f"\nHierarchical Vehicle Replacement analysis saved to: output/Vehicle_Replacement_Hierarchical.xlsx")
    
    # Display sample of hierarchical structure
    print("\n=== 2026 HIERARCHICAL SUMMARY SAMPLE ===")
    print("LOB/Vehicle Class                | 2026 Vehicle Count | 2026 Replacement Cost (Est.)")
    print("-" * 85)
    
    # Show first few rows as sample
    for i, row in enumerate(combined_data[:15]):  # Show first 15 rows
        lob_vc = row['LOB/Vehicle Class'][:25]  # Truncate long names
        count_2026 = row.get('2026 Vehicle Count', 0)
        spend_2026 = row.get('2026 Replacement Cost (Est.)', 0)
        print(f"{lob_vc:<32} | {count_2026:>16} | ${spend_2026:>14,.0f}")
    
    print("... (showing first 15 rows)")
    print(f"\nTotal rows in analysis: {len(combined_data)}")
    
    return hierarchical_pivot

if __name__ == "__main__":
    # Execute the EV Assumption analysis using pivot tables
    ev_output_file = create_ev_assumption_pivot_table()
    print(f"\nCompleted EV Assumption! Output file: {ev_output_file}")
    
    # Execute Radio Installation analysis by LOB
    print("\n" + "="*60)
    count_pivot, spend_pivot = create_radio_pivot_table()
    
    # Execute Vehicle Replacement analysis by LOB and Vehicle Class (Hierarchical)
    print("\n" + "="*60)
    hierarchical_pivot = create_vehicle_replacement_hierarchical_pivot_table()
    
    # Execute Detailed Vehicle Replacement analysis by LOB, Vehicle Class, and ObjectType
    print("\n" + "="*60)
    detailed_hierarchical_pivot = create_detailed_vehicle_replacement_hierarchical_pivot_table()
    
    # Execute L.H.P and ObjectType Vehicle Replacement analysis
    print("\n" + "="*60)
    lhp_object_pivot = create_lhp_object_type_pivot_table()
    
    # Execute ObjectType-Only Vehicle Replacement analysis
    print("\n" + "="*60)
    object_type_only_pivot = create_object_type_only_pivot_table()
    
    # Note: All dedicated EV analyses (Freightliner, Van, Car/SUV, Pickup) are now
    # integrated into the main EV_ASSUMPTION_Analysis.xlsx file as separate sheets
