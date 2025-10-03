"""
Simple CSV Data Validator and Reporter (Dependency-Free)

This script validates a CSV file against a predefined schema, checking for
missing values and ensuring columns adhere to expected data types (string, int, float).
It generates a report of all invalid entries found.

The schema is hardcoded for demonstration and can be easily customized.

Usage:
    python csv_data_validator.py <csv_filepath>

<csv_filepath>: Path to the CSV file to validate.
"""

import sys
import csv
from typing import List, Dict, Any, Tuple

# --- CONFIGURATION ---
# Define the expected schema for the CSV file.
# Keys are column names, values are expected data types as strings.
DATA_SCHEMA = {
    "ID": "int",
    "Name": "str",
    "Email": "str",
    "Age": "int",
    "Salary": "float",
    "IsActive": "bool"
}
# ---------------------

def safe_cast(value: str, target_type: str) -> Tuple[Any, bool]:
    """
    Attempts to cast a string value to the target type and reports success.

    Args:
        value (str): The string value to cast.
        target_type (str): The name of the expected type ('int', 'float', 'str', 'bool').

    Returns:
        tuple: (The casted value or original value, True if cast succeeded, False otherwise).
    """
    value = value.strip()
    if not value:
        return value, False # Treat empty string as failed cast/invalid

    try:
        if target_type == "int":
            return int(float(value)), True  # Handles '10.0' being passed as int
        elif target_type == "float":
            return float(value), True
        elif target_type == "str":
            return value, True
        elif target_type == "bool":
            # Simple conversion for common boolean representations
            if value.lower() in ('true', 't', '1', 'yes', 'y'):
                return True, True
            if value.lower() in ('false', 'f', '0', 'no', 'n'):
                return False, True
            return value, False # Failed to match known boolean value
        else:
            return value, False # Unknown type
    except ValueError:
        return value, False
    except TypeError:
        return value, False


def validate_csv(filepath: str, schema: Dict[str, str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Reads a CSV file and validates it against the schema.

    Args:
        filepath (str): Path to the CSV file.
        schema (Dict[str, str]): The validation schema (Column -> Type).

    Returns:
        tuple: (list of error records, list of header issues).
    """
    errors: List[Dict[str, Any]] = []
    header_issues: List[str] = []
    expected_headers = set(schema.keys())

    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            try:
                # Read the header row
                headers = [h.strip() for h in next(reader)]
            except StopIteration:
                return errors, ["CSV file is empty."]

            # --- Header Validation ---
            actual_headers = set(headers)
            missing_headers = expected_headers - actual_headers
            extra_headers = actual_headers - expected_headers

            if missing_headers:
                header_issues.append(f"Missing required columns: {', '.join(missing_headers)}")
            if extra_headers:
                header_issues.append(f"Found unexpected columns: {', '.join(extra_headers)}")
            if header_issues:
                # If headers are wrong, we can't reliably process the data rows
                return errors, header_issues

            # --- Data Row Validation ---
            for row_num, row in enumerate(reader, start=2): # start=2 because row 1 is the header
                row_errors = []
                record = {}
                
                # Zip headers and row data, using None for missing cells
                for i, header in enumerate(headers):
                    value = row[i] if i < len(row) else ''
                    record[header] = value

                    # Only check against schema if the header is expected
                    if header in schema:
                        expected_type = schema[header]
                        casted_value, is_valid = safe_cast(value, expected_type)

                        if not value.strip():
                            row_errors.append(f"Missing Value in '{header}'")
                        elif not is_valid:
                            row_errors.append(f"Type Mismatch in '{header}'. Expected '{expected_type}', found '{value}'")
                
                if row_errors:
                    errors.append({
                        "row": row_num,
                        "data": record,
                        "issues": row_errors
                    })
        
    except FileNotFoundError:
        print(f"\nError: File not found at '{filepath}'")
        sys.exit(1)
    except csv.Error as e:
        print(f"\nError reading CSV file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

    return errors, header_issues


def generate_report(filepath: str, errors: List[Dict[str, Any]], header_issues: List[str]):
    """
    Prints a formatted validation report to the console.
    """
    total_errors = len(errors)
    total_issues = total_errors + len(header_issues)

    print("=" * 70)
    print(" " * 15 + "CSV DATA VALIDATION REPORT")
    print("=" * 70)
    print(f"File: {filepath}")
    print(f"Schema Used: {DATA_SCHEMA}")
    print("-" * 70)
    
    if total_issues == 0:
        print("\n✅ VALIDATION PASSED! No issues found based on the defined schema.")
        print("-" * 70)
        return

    print(f"\n⚠️ VALIDATION FAILED! Total Issues Found: {total_issues}\n")

    if header_issues:
        print("--- HEADER ISSUES ---")
        for issue in header_issues:
            print(f"    - {issue}")
        print("-" * 70)

    if errors:
        print("--- RECORD VALIDATION ERRORS ---")
        print(f"Found {total_errors} rows with data errors.")
        for error in errors:
            print(f"\n[ROW {error['row']}]")
            for issue in error['issues']:
                print(f"    - {issue}")
            
            # Optional: Show the problematic record data
            # print("    Data:", error['data'])

        print("-" * 70)


def main():
    """Handles command-line interface logic."""
    if len(sys.argv) != 2:
        print(__doc__) # Print the script's docstring for usage instructions
        sys.exit(1)

    filepath = sys.argv[1]

    # Run the validation
    errors, header_issues = validate_csv(filepath, DATA_SCHEMA)

    # Generate the report
    generate_report(filepath, errors, header_issues)


if __name__ == "__main__":
    main()
