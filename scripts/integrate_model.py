import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from peft import PeftModel
import os
from map_categories import map_columns_to_categories

# Load fine-tuned model and tokenizer
model_path = "C:/Users/Utsav.Mehta/Thinkathon/thinkathon-invincible/models/recommendation_model"
t5_model_path = "C:/Users/Utsav.Mehta/Thinkathon/thinkathon-invincible/models/t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_path)
base_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)
model = PeftModel.from_pretrained(base_model, model_path)

model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Example function to convert patient row into prompt string
def format_patient_prompt(row):
    parts = []
    for col in df_features.columns:
        val = row.get(col)
        if pd.notna(val):
            parts.append(f"{col}: {val}")
    prompt = "; ".join(parts)
    return prompt

# Generate recommendation using the fine-tuned T5
def generate_recommendation(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}  # move to device
    outputs = model.generate(**inputs, max_length=max_length, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Apply on your DataFrame
def add_ai_recommendations(df, feature_cols):
    global df_features
    df_features = df[feature_cols]  # keep features subset handy
    
    # Map the feature columns to categories
    category_columns = map_columns_to_categories(feature_cols)
    
    # Prepare a list to hold recommendations per category per row
    category_recommendations = {cat: [] for cat in category_columns}
    
    for _, row in df.iterrows():
        for category, cols in category_columns.items():
            # Extract the subset of features relevant to this category
            category_data = row[cols]
            
            # Format prompt based only on category data
            prompt = format_patient_prompt(category_data)
            
            try:
                rec = generate_recommendation(prompt)
            except Exception as e:
                rec = f"Error generating recommendation: {e}"
            
            category_recommendations[category].append(rec)
    
    # Add a new column for each category with its recommendations
    for category, recs in category_recommendations.items():
        col_name = f"AI_Recommendation_{category.replace(' ', '_')}"
        df[col_name] = recs
    
    return df
