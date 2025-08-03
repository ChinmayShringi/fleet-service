import pandas as pd
import shutil
import os

def calculate_vehicle_data():
    """Calculate vehicle counts and replacement costs for H, L, P categories from data.xlsx"""
    # Read the data Excel file
    df_data = pd.read_excel('data.xlsx')
    
    # Calculate counts for each vehicle class where 2026 Forecast Count = 1
    forecast_2026 = df_data['2026 Forecast Count'] == 1
    
    count_H = len(df_data[(forecast_2026) & (df_data['L.H.P'] == 'H')])
    count_L = len(df_data[(forecast_2026) & (df_data['L.H.P'] == 'L')])
    count_P = len(df_data[(forecast_2026) & (df_data['L.H.P'] == 'P')])
    
    # Calculate replacement costs for each vehicle class where 2026 Forecast Count = 1
    # Handle NaN values by filling them with 0 before summing
    replacement_cost_col = '2026 Replacement Cost'
    
    cost_H = df_data[(forecast_2026) & (df_data['L.H.P'] == 'H')][replacement_cost_col].fillna(0).sum()
    cost_L = df_data[(forecast_2026) & (df_data['L.H.P'] == 'L')][replacement_cost_col].fillna(0).sum()
    cost_P = df_data[(forecast_2026) & (df_data['L.H.P'] == 'P')][replacement_cost_col].fillna(0).sum()
    
    print(f"Vehicle counts for 2026 (where Forecast Count = 1):")
    print(f"H vehicles: {count_H}")
    print(f"L vehicles: {count_L}")
    print(f"P vehicles: {count_P}")
    print(f"Total: {count_H + count_L + count_P}")
    
    print(f"\n2026 Replacement Costs (where Forecast Count = 1):")
    print(f"H vehicles: ${cost_H:,.2f}")
    print(f"L vehicles: ${cost_L:,.2f}")
    print(f"P vehicles: ${cost_P:,.2f}")
    print(f"Total: ${cost_H + cost_L + cost_P:,.2f}")
    
    return count_H, count_L, count_P, cost_H, cost_L, cost_P

def fill_ev_assumption_template():
    """Fill the EV_ASSUMPTION template with calculated vehicle counts and replacement costs"""
    
    # Calculate the vehicle counts and replacement costs
    count_H, count_L, count_P, cost_H, cost_L, cost_P = calculate_vehicle_data()
    
    # Read the template
    df_template = pd.read_excel('templates/EV_ASSUMPTION.xlsx')
    
    # Fill the counts in the appropriate cells:
    # Based on template structure: H is at index 5, L is at index 6, P is at index 7
    # B6 (row index 5, column index 1): H vehicle count
    # B7 (row index 6, column index 1): L vehicle count  
    # B8 (row index 7, column index 1): P vehicle count
    
    df_template.iloc[5, 1] = count_H  # Row 6 (B6) - H vehicles
    df_template.iloc[6, 1] = count_L  # Row 7 (B7) - L vehicles
    df_template.iloc[7, 1] = count_P  # Row 8 (B8) - P vehicles
    
    # Fill the replacement costs in the appropriate cells:
    # C6 (row index 5, column index 2): H replacement cost
    # C7 (row index 6, column index 2): L replacement cost  
    # C8 (row index 7, column index 2): P replacement cost
    
    df_template.iloc[5, 2] = cost_H  # Row 6 (C6) - H replacement cost
    df_template.iloc[6, 2] = cost_L  # Row 7 (C7) - L replacement cost
    df_template.iloc[7, 2] = cost_P  # Row 8 (C8) - P replacement cost
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Save the filled template to output folder
    output_path = 'output/EV_ASSUMPTION_filled.xlsx'
    df_template.to_excel(output_path, index=False, header=False)
    
    print(f"\nTemplate filled and saved to: {output_path}")
    print(f"Vehicle Counts filled:")
    print(f"  B7 (H vehicles): {count_H}")
    print(f"  B8 (L vehicles): {count_L}")
    print(f"  B9 (P vehicles): {count_P}")
    print(f"Replacement Costs filled:")
    print(f"  C7 (H cost): ${cost_H:,.2f}")
    print(f"  C8 (L cost): ${cost_L:,.2f}")
    print(f"  C9 (P cost): ${cost_P:,.2f}")
    
    return output_path

if __name__ == "__main__":
    # Execute the main function
    output_file = fill_ev_assumption_template()
    print(f"\nCompleted! Output file: {output_file}")
