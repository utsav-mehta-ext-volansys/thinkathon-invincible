import pandas as pd
import random
import datasets
import evaluate
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)
import torch
import numpy as np
from peft import get_peft_model, LoraConfig, TaskType, PeftModel
import os
import sys
import contextlib

# --- Step 1: Load ranges from Excel ---
def load_ranges_from_excel(file_path):
    xls = pd.ExcelFile(file_path)
    all_ranges = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        df.columns = [col.strip() for col in df.columns]
        if 'Parameter' in df.columns:
            param_col = 'Parameter'
        elif 'Value' in df.columns:
            param_col = 'Value'
        else:
            print(f"Sheet '{sheet}' missing 'Parameter' or 'Value' column. Skipping.")
            continue
        if 'Unit' not in df.columns:
            df['Unit'] = ""
        param_dict = {}
        for _, row in df.iterrows():
            param = row[param_col]
            low = row.get('Low', None)
            high = row.get('High', None)
            unit = row.get('Unit', "")
            if pd.isna(param):
                continue
            param_dict[param] = (low, high, unit if pd.notna(unit) else "")
        all_ranges[sheet] = param_dict
    return all_ranges

# --- Step 2: Generate synthetic examples ---
def generate_synthetic_examples(param_dict, sheet_name, num_examples=50):
    params = list(param_dict.keys())
    examples = []

    for example_num in range(num_examples):
        print(f"\n--- Generating Example {example_num + 1} ---")
        input_parts = []
        abnormalities = []

        for param in params:
            low, high, unit = param_dict[param]
            print(f"Param: {param} | Low: {low} | High: {high} | Unit: {unit}")

            # Case 1: Low/High range is missing
            if pd.isna(low) or pd.isna(high):
                val = round(random.uniform(1, 100), 2)
                status = 'normal'
                print(f"  → No range. Generated {val} (assumed normal)")
            else:
                # Decide if we generate normal (70%) or abnormal (30%) value
                if random.random() < 0.7:
                    # Generate normal value
                    val = round(random.uniform(low, high), 2)
                else:
                    # Generate abnormal value
                    if random.random() < 0.5:
                        val = round(low * 0.8, 2)  # below normal
                    else:
                        val = round(high * 1.2, 2)  # above normal

                # Determine actual status
                if val < low:
                    status = 'low'
                elif val > high:
                    status = 'high'
                else:
                    status = 'normal'

                print(f"  → Generated value: {val} | Status: {status} | Expected Range: ({low} - {high})")

            input_parts.append(f"{param}: {val} {unit}".strip())

            if status != 'normal':
                abnormalities.append((param, status))

        # Construct suggestion
        if not abnormalities:
            suggestion = f"All {sheet_name} parameters are within normal ranges. Maintain a healthy lifestyle."
        else:
            parts = []
            for p, st in abnormalities:
                if st == 'low':
                    parts.append(f"{p} is below normal, consider consulting your healthcare provider.")
                else:
                    parts.append(f"{p} is above normal, lifestyle changes or medical advice recommended.")
            suggestion = " ".join(parts)

        input_text = "; ".join(input_parts)
        input_text = f"analyze: {input_text}"  # Task prefix for models like T5

        print(f"Final Input: {input_text}")
        print(f"Suggestion: {suggestion}")

        examples.append((input_text, suggestion))

    return examples
# --- Step 3: Prepare dataset ---
def prepare_dataset(file_path, examples_per_sheet=50):
    all_ranges = load_ranges_from_excel(file_path)
    dataset = {"input_text": [], "target_text": []}

    for sheet, param_dict in all_ranges.items():
        examples = generate_synthetic_examples(param_dict, sheet, examples_per_sheet)
        for inp, tgt in examples:
            dataset["input_text"].append(inp)
            dataset["target_text"].append(tgt)

    return dataset

# --- Step 4: Preprocess for T5 ---
def preprocess_for_t5(tokenizer, dataset, max_len=512):
    def preprocess_function(examples):
        inputs = tokenizer(examples["input_text"], truncation=True, padding="max_length", max_length=max_len)
        targets = tokenizer(examples["target_text"], truncation=True, padding="max_length", max_length=max_len)

        labels = targets["input_ids"]
        labels = [
            [(label if label != tokenizer.pad_token_id else -100) for label in label_seq]
            for label_seq in labels
        ]

        inputs["labels"] = labels
        return inputs

    ds = datasets.Dataset.from_dict(dataset)
    tokenized_ds = ds.map(preprocess_function, batched=True)
    return tokenized_ds

# --- Step 5: Split dataset ---
def train_val_split(tokenized_dataset, val_ratio=0.1):
    train_test = tokenized_dataset.train_test_split(test_size=val_ratio, seed=42)
    return train_test['train'], train_test['test']

# --- Step 6: Fine-tune T5 with LoRA PEFT ---
def fine_tune_peft(train_ds, val_ds, output_dir="./recommendation_model_test_new", epochs=8):
    model_name = "./t5-small"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    base_model = T5ForConditionalGeneration.from_pretrained(model_name)

    # LoRA config
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q", "v"],  # Common for T5 attention layers
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.SEQ_2_SEQ_LM
    )

    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()

    # Data collator for seq2seq
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        eval_strategy="no",   # Disable evaluation
        num_train_epochs=1,
        logging_steps=5,
        save_steps=9999999,   # Don't save
        learning_rate=5e-4,
        seed=42
    )

    def compute_metrics(eval_pred):
        metric = evaluate.load("rouge")
        predictions, labels = eval_pred

        if isinstance(predictions, tuple):  # Handle Trainer output
            predictions = predictions[0]
        pred_ids = np.argmax(predictions, axis=-1)  # shape: (batch, seq_len)


        # Decode predictions
        decoded_preds = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)

        # Replace -100 with pad_token_id and decode labels
        cleaned_labels = [
            [token if token != -100 else tokenizer.pad_token_id for token in label_seq]
            for label_seq in labels
        ]
        decoded_labels = tokenizer.batch_decode(cleaned_labels, skip_special_tokens=True)

        # Compute ROUGE
        result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)

        result = {k: round(v * 100, 2) for k, v in result.items() if isinstance(v, float)}
        return result


    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"fine-tuned and saved at {output_dir}")

    return model, tokenizer

# --- Step 7: Inference ---
def infer(model, tokenizer, input_text):
    # Add prefix for consistency
    input_text = "analyze: " + input_text
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    outputs = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=100,
        num_beams=4,
        early_stopping=True,
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# --- Main Execution ---
if __name__ == "__main__":
    excel_file = "reference_excel.xlsx"  # Update this to your real file path
    output_log = "debug_output.txt" 

    with open(output_log, "w", encoding="utf-8") as f, contextlib.redirect_stdout(f):

        # prepare dataset
        dataset_dict = prepare_dataset(excel_file, examples_per_sheet=50)

        # pre-process tokenized model
        tokenized_dataset = preprocess_for_t5(T5Tokenizer.from_pretrained("./t5-small"), dataset_dict)

        # split train and val dataset
        train_dataset, val_dataset = train_val_split(tokenized_dataset, val_ratio=0.1)

        # fine tuning model
        model, tokenizer = fine_tune_peft(train_dataset, val_dataset, epochs=8)

        # trying test input

        test_input = ("White Blood Cells: 7695.25; Neutrophils (%): 56.22 %; Lymphs (%): 29.3 %; Monocytes (%): 12.0 %; "
                    "Eos (%): 1.93 %; Basos (%): 0.39 %; Platelets: 309636.87; Red Blood Cells: 4.23; Hemoglobin: 13.39; "
                    "HCT (Hematocrit): 43.35; Mean Corpuscular Volume: 120.0; Mean Corpuscular Hemoglobin: 28.84; "
                    "Mean Corpuscular Hemoglobin Concentration: 43.2; RDW: 11.43 %; Neutrophils (Absolute): 6.5; "
                    "Lymphs (Absolute): 0.83; Monocytes(Absolute): 0.74; Eos (Absolute): 0.32; Baso (Absolute): 0.2; "
                    "Immature Granulocytes: 21; Immature Grans (Abs): 8")

        result = infer(model, tokenizer, test_input)
        print("Model Output:\n", result)
