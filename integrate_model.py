import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load fine-tuned model + tokenizer
model_name_or_path = "./t5_finetuned"  # update to your model path
tokenizer = T5Tokenizer.from_pretrained(model_name_or_path)
model = T5ForConditionalGeneration.from_pretrained(model_name_or_path)
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
    parts.append(f"Abnormal tests count: {row.get('Abnormal_count', 0)}")
    prompt = "; ".join(parts)
    return prompt

# Generate recommendation using the fine-tuned T5
def generate_recommendation(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(device)
    outputs = model.generate(**inputs, max_length=max_length, num_beams=5, early_stopping=True)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

# Apply on your DataFrame
def add_ai_recommendations(df, feature_cols):
    global df_features
    df_features = df[feature_cols]  # keep features subset handy
    
    recommendations = []
    for _, row in df.iterrows():
        prompt = format_patient_prompt(row)
        try:
            rec = generate_recommendation(prompt)
        except Exception as e:
            rec = f"Error generating recommendation: {e}"
        recommendations.append(rec)
    
    df['AI_Recommendation'] = recommendations
    return df

# Usage:
feature_cols = df_features.columns.tolist() + ['Abnormal_count']  # Ensure 'Abnormal_count' is included
df = add_ai_recommendations(df, feature_cols)

# Now df has a new column 'AI_Recommendation' with generated suggestions
