import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from peft import PeftModel

# Load fine-tuned model and tokenizer
model_path = "./recommendation_model"
# tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
tokenizer = T5Tokenizer.from_pretrained("./recommendation_model")
base_model = T5ForConditionalGeneration.from_pretrained("t5-small")
model = PeftModel.from_pretrained(base_model, "./recommendation_model")

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
    # parts.append(f"Abnormal tests count: {row.get('Abnormal_count', 0)}")
    prompt = "; ".join(parts)
    return prompt

# Generate recommendation using the fine-tuned T5
def generate_recommendation(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    print("inputs",inputs)
    inputs = {k: v.to(device) for k, v in inputs.items()}  # move to device
    outputs = model.generate(**inputs, max_length=max_length, num_beams=5, early_stopping=True)
    print("outputs",outputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Apply on your DataFrame
def add_ai_recommendations(df, feature_cols):
    global df_features
    df_features = df[feature_cols]  # keep features subset handy
    
    recommendations = []
    for _, row in df.iterrows():
        prompt = format_patient_prompt(row)
        print("prompt",prompt)
        try:
            rec = generate_recommendation(prompt)
            print("rec",rec)
        except Exception as e:
            rec = f"Error generating recommendation: {e}"
        recommendations.append(rec)
    
    df['AI_Recommendation'] = recommendations
    return df

# Usage:
# feature_cols = df_features.columns.tolist() + ['Abnormal_count']  # Ensure 'Abnormal_count' is included
# df = add_ai_recommendations(df, feature_cols)

# Now df has a new column 'AI_Recommendation' with generated suggestions
