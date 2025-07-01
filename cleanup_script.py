import pandas as pd
import os
from map_categories import map_columns_to_categories
from prepare_ml_data import prepare_data

def read_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    # Try to read as Excel
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        print("File read as Excel.")
        return df
    except Exception as e:
        print(f"Not Excel: {e}")

    # Try to read as CSV
    try:
        df = pd.read_csv(filepath)
        print("File read as CSV.")
        return df
    except Exception as e:
        print(f"Not CSV: {e}")

    # Try to read as PDF (returns text instead of DataFrame)
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        print("File read as PDF.")
        return text
    except Exception as e:
        print(f"Not PDF: {e}")

    raise ValueError("Unsupported or unreadable file format.")


def read_ref_file(filepath):
    return pd.read_excel(filepath, sheet_name=None)  # Returns dict of DataFrames

def flag_out_of_range(df, reference_df_dict, category_mapping):
    for category, columns in category_mapping.items():
        if category not in reference_df_dict:
            print(f"Category '{category}' not found in reference Excel sheets.")
            continue

        category_df = reference_df_dict[category].set_index("Value")
        for col in columns:
            if col not in df.columns:
                print(f"Column '{col}' not found in CSV data.")
                continue
            if col not in category_df.index:
                print(f"Column '{col}' not found in reference sheet for category '{category}'.")
                continue

            try:
                low = category_df.at[col, "Low"]
                high = category_df.at[col, "High"]

                def check_range(val):
                    try:
                        val = float(val)
                        if val < low:
                            return "Low"
                        elif val > high:
                            return "High"
                        else:
                            return ""
                    except:
                        return "Invalid"

                df[f"{col}_Flag"] = df[col].apply(check_range)
            except Exception as e:
                print(f"Error processing column '{col}': {e}")
    return df

# --- Main Execution ---
def main():
    file_path = input("Enter path to your CSV file: ").strip()

    if not os.path.exists(file_path):
        print("File not found.")
        return

    try:
        df = read_file(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    try:
        reference_sheets = read_ref_file("Template for report_new.xlsx")
    except Exception as e:
        print(f"Error reading reference file: {e}")
        return

    column_names = df.columns.tolist()
    category_mapping = map_columns_to_categories(column_names)

    print("\n=== Mapped Health Categories from CSV ===")
    for category, cols in category_mapping.items():
        print(f"\n{category}:")
        for col in cols:
            print(f"  - {col}")

    # Perform range checking and flagging
    df = flag_out_of_range(df, reference_sheets, category_mapping)
    # Save final result
    output_path = "results_with_flags.csv"
    ml_path = "ml_input.csv"
    df.to_csv(output_path, index=False)
    print(f"\nProcessed file saved to: {output_path}")
    # ml_df = prepare_data(df)
    prepare_data(df)
    # ml_df.to_csv(ml_path, index=False)

if __name__ == "__main__":
    main()
