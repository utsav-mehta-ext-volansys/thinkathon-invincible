import pandas as pd
import os

# --- Category Definitions ---
health_categories = {
    "CBC": {
        "Hemoglobin", "Platelets", "White Blood Cells", "Red Blood Cells", "Hematocrit",
        "Mean Corpuscular Volume", "Mean Corpuscular Hemoglobin", "Mean Corpuscular Hemoglobin Concentration"
    },
    "Lipid Profile": {
        "Cholesterol", "Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"
    },
    "Blood Glucose Levels": {
        "Glucose", "HbA1c", "Insulin"
    },
    "Organ Function Tests": {
        "ALT", "AST", "ALP", "Creatinine", "GFR", "C-reactive Protein"
    },
    "Urine Test": {
        "Urine Protein", "Urine Glucose", "Urine Ketones", "Urine pH", "Specific Gravity",
        "Nitrites", "Leukocyte Esterase"
    },
    "Vitals": {
        "BMI", "Systolic Blood Pressure", "Diastolic Blood Pressure", "Heart Rate"
    },
    "Cardiac Markers": {
        "Troponin"
    }
}

# --- Mapper Function ---
def map_columns_to_categories(column_names):
    result = {category: [] for category in health_categories}

    for col in column_names:
        matched = False
        for category, known_features in health_categories.items():
            if col.strip() in known_features:
                result[category].append(col.strip())
                matched = True
                break
        if not matched:
            result.setdefault("Uncategorized", []).append(col.strip())

    return {cat: cols for cat, cols in result.items() if cols}

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


# --- Main Execution ---
def main():
    import os

    file_path = input("Enter path to your CSV file: ").strip()

    if not os.path.exists(file_path):
        print("File not found.")
        return

    try:
        df = read_file(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    column_names = df.columns.tolist()
    category_mapping = map_columns_to_categories(column_names)

    print("\n=== Mapped Health Categories from CSV ===")
    for category, cols in category_mapping.items():
        print(f"\n{category}:")
        for col in cols:
            print(f"  - {col}")

if __name__ == "__main__":
    main()
