from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel

tokenizer = T5Tokenizer.from_pretrained("./recommendation_model")
base_model = T5ForConditionalGeneration.from_pretrained("t5-small")
model = PeftModel.from_pretrained(base_model, "./recommendation_model")

input_text = """White Blood Cells: 7695.25; Neutrophils (%): 56.22 %; Lymphs (%): 29.3 %; Monocytes (%): 12.0 %; Eos (%): 1.93 %; Basos (%): 0.39 %; Platelets: 309636.87; Red Blood Cells: 4.23; Hemoglobin: 13.39; HCT (Hematocrit): 43.35; Mean Corpuscular Volume: 120.0; Mean Corpuscular Hemoglobin: 28.84; Mean Corpuscular Hemoglobin Concentration: 43.2; RDW: 11.43 %; Neutrophils (Absolute): 6.5; Lymphs (Absolute): 0.83; Monocytes(Absolute): 0.74; Eos (Absolute): 0.32; Baso (Absolute): 0.2; Immature Granulocytes: 21; Immature Grans (Abs): 8"""
# input_text = "analyze: " + input_text

tokens = tokenizer.tokenize(input_text)
# print("🔢 Input token length:", len(tokens))
# Tokenize with a large enough max_length
inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)

# Generate with controlled output length
outputs = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_new_tokens=100,           # Adjust to allow full-length suggestion
    num_beams=4,                  # Beam search for better quality
    early_stopping=True
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
