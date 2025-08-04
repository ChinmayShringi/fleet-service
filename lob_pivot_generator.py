"""
LOB Equipment Lifecycle Pivot Table Generator

This script creates a pivot table showing equipment grouped by LOB (Line of Business)
with their corresponding lifecycle information from OOL.xlsx.
"""

from ool_reader import create_lob_lifecycle_pivot

def main():
    """Generate LOB pivot table"""
    print("LOB Equipment Lifecycle Pivot Table Generator")
    print("=" * 60)
    
    # Generate the pivot table
    pivot_data = create_lob_lifecycle_pivot()
    
    if pivot_data:
        print("\nPivot table generated successfully!")
        print(f"Data includes {len(pivot_data)} LOBs")
    else:
        print("\nFailed to generate pivot table.")

if __name__ == "__main__":
    main()