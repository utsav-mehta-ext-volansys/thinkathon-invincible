import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from peft import PeftModel
from map_categories import map_columns_to_categories

# Paths
model_path = "C:/Users/Utsav.Mehta/Thinkathon/thinkathon-invincible/recommendation_model"
t5_model_path = "C:/Users/Utsav.Mehta/Thinkathon/thinkathon-invincible/t5-small"
reference_excel_path = "C:/Users/Utsav.Mehta/Thinkathon/thinkathon-invincible/reference_excel.xlsx"

# Load model and tokenizer
tokenizer = T5Tokenizer.from_pretrained(model_path)
base_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)
model = PeftModel.from_pretrained(base_model, model_path)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load reference sheet as dictionary of parameter ranges and units
def load_reference_excel(path):
    xls = pd.ExcelFile(path)
    ref_data = {}

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        df.columns = [col.strip() for col in df.columns]

        if 'Parameter' in df.columns:
            key_col = 'Parameter'
        elif 'Value' in df.columns:
            key_col = 'Value'
        else:
            continue

        if 'Unit' not in df.columns:
            df['Unit'] = ""

        sheet_dict = {}
        for _, row in df.iterrows():
            param = row[key_col]
            low = row.get('Low', None)
            high = row.get('High', None)
            unit = row.get('Unit', "")
            if pd.notna(param):
                sheet_dict[param] = (low, high, unit)
        ref_data[sheet] = sheet_dict

    return ref_data

# Generate model recommendation
def generate_recommendation(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model.generate(**inputs, max_length=max_length, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Build final structured output
def build_structured_recommendations(df):
    reference_sheets = load_reference_excel(reference_excel_path)
    category_mapping = map_columns_to_categories(df.columns.tolist())
    results = []

    for _, row in df.iterrows():
        for category, param_dict in reference_sheets.items():
            values = {}

            category_cols = category_mapping.get(category, [])
            if not category_cols:
                continue

            prompt_parts = []
            for param in category_cols:
                if param in row and pd.notna(row[param]):
                    val = row[param]
                    prompt_parts.append(f"{param}: {val}")
                    values[param] = str(val)

            if not values:
                continue

            prompt = "analyze: " + "; ".join(prompt_parts)
            try:
                recommendation = generate_recommendation(prompt)
            except Exception as e:
                recommendation = f"Error generating recommendation: {e}"

            results.append({
                "name": category,
                "values": values,
                "recommendation": recommendation
            })

    return {"tests": results}