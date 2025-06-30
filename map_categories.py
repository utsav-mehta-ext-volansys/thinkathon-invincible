# --- Category Definitions ---
health_categories = {
    "CBC": {
        "Hemoglobin", "Platelets", "White Blood Cells", "Red Blood Cells", "Hematocrit",
        "Mean Corpuscular Volume", "Mean Corpuscular Hemoglobin", "Mean Corpuscular Hemoglobin Concentration"
    },
    "Lipid Profile": {
        "Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"
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

# Canonical aliases with lowercase keys for case-insensitive matching
column_aliases = {
    "hb": "Hemoglobin",
    "hgb": "Hemoglobin",
    "hemoglobin": "Hemoglobin",

    "plt": "Platelets",
    "platelet count": "Platelets",
    "platelets": "Platelets",

    "wbc": "White Blood Cells",
    "leukocytes": "White Blood Cells",
    "white blood cells": "White Blood Cells",

    "rbc": "Red Blood Cells",
    "red blood cells": "Red Blood Cells",

    "hct": "Hematocrit",
    "hematocrit": "Hematocrit",

    "mcv": "Mean Corpuscular Volume",
    "mean corpuscular volume": "Mean Corpuscular Volume",

    "mch": "Mean Corpuscular Hemoglobin",
    "mean corpuscular hemoglobin": "Mean Corpuscular Hemoglobin",

    "mchc": "Mean Corpuscular Hemoglobin Concentration",
    "mean corpuscular hemoglobin concentration": "Mean Corpuscular Hemoglobin Concentration",

    "cholesterol": "Total Cholesterol",
    "total cholesterol": "Total Cholesterol",

    "ldl": "LDL Cholesterol",
    "ldl cholesterol": "LDL Cholesterol",

    "hdl": "HDL Cholesterol",
    "hdl cholesterol": "HDL Cholesterol",

    "triglycerides": "Triglycerides",

    "glucose": "Glucose",
    "blood sugar": "Glucose",

    "hba1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",

    "insulin": "Insulin",

    "alt": "ALT",
    "sgpt": "ALT",

    "ast": "AST",
    "sgot": "AST",

    "alp": "ALP",
    "creatinine": "Creatinine",
    "gfr": "GFR",
    "egfr": "GFR",

    "crp": "C-reactive Protein",
    "c-reactive protein": "C-reactive Protein",

    "urine protein": "Urine Protein",
    "protein (urine)": "Urine Protein",

    "urine glucose": "Urine Glucose",
    "glucose (urine)": "Urine Glucose",

    "urine ketones": "Urine Ketones",
    "ketones (urine)": "Urine Ketones",

    "urine ph": "Urine pH",
    "specific gravity": "Specific Gravity",
    "nitrites": "Nitrites",
    "leukocyte esterase": "Leukocyte Esterase",

    "bmi": "BMI",
    "body mass index": "BMI",

    "systolic": "Systolic Blood Pressure",
    "systolic bp": "Systolic Blood Pressure",
    "systolic blood pressure": "Systolic Blood Pressure",

    "diastolic": "Diastolic Blood Pressure",
    "diastolic bp": "Diastolic Blood Pressure",
    "diastolic blood pressure": "Diastolic Blood Pressure",

    "pulse": "Heart Rate",
    "heart rate": "Heart Rate",

    "troponin": "Troponin"
}


# --- Mapper Function ---
def map_columns_to_categories(column_names):
    result = {category: [] for category in health_categories}
    result["Uncategorized"] = []

    for raw_col in column_names:
        col = raw_col.strip()
        col_lower = col.lower()

        canonical = column_aliases.get(col_lower)
        if canonical:
            matched = False
            for category, features in health_categories.items():
                if canonical in features:
                    result[category].append(col)
                    matched = True
                    break
            if not matched:
                result["Uncategorized"].append(col)
        else:
            result["Uncategorized"].append(col)

    return {cat: cols for cat, cols in result.items() if cols}
