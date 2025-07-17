import pandas as pd
import random
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    TrainingArguments,
    Trainer
)
from datasets import Dataset
from peft import get_peft_model, LoraConfig, TaskType
import torch


# --- Load Ranges from Excel ---
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


# --- Generate synthetic examples ---
def generate_synthetic_examples(param_dict, sheet_name, num_examples=20):
    params = list(param_dict.keys())
    examples = []

    for _ in range(num_examples):
        input_parts = []
        abnormalities = []

        for param in params:
            low, high, unit = param_dict[param]

            if random.random() < 0.7:
                if pd.isna(low) or pd.isna(high):
                    val = random.randint(1, 100)
                    status = 'normal'
                else:
                    val = round(random.uniform(low, high), 2)
                    status = 'normal'
            else:
                if pd.isna(low) or pd.isna(high):
                    val = round(random.uniform(1, 100), 2)
                    status = 'normal'
                else:
                    if random.random() < 0.5:
                        val = round(low * 0.8, 2)
                        status = 'low'
                    else:
                        val = round(high * 1.2, 2)
                        status = 'high'

            input_parts.append(f"{param}: {val} {unit}".strip())

            if status != 'normal':
                abnormalities.append((param, status))

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
        examples.append((input_text, suggestion))

    return examples


# --- Prepare dataset ---
def prepare_dataset(file_path, examples_per_sheet=20):
    all_ranges = load_ranges_from_excel(file_path)
    dataset = {"input_text": [], "target_text": []}

    for sheet, param_dict in all_ranges.items():
        examples = generate_synthetic_examples(param_dict, sheet, examples_per_sheet)
        for inp, tgt in examples:
            print("inp------------------------------",inp)
            print("tgt-------------------------------",tgt)
            dataset["input_text"].append(inp)
            dataset["target_text"].append(tgt)

    return dataset


# --- Tokenize ---
def tokenize_dataset(dataset_dict, tokenizer, max_len=128):
    def tokenize(example):
        input_enc = tokenizer(
            example["input_text"],
            padding="max_length",
            truncation=True,
            max_length=max_len
        )
        target_enc = tokenizer(
            example["target_text"],
            padding="max_length",
            truncation=True,
            max_length=max_len
        )
        input_enc["labels"] = [
            (label if label != tokenizer.pad_token_id else -100)
            for label in target_enc["input_ids"]
        ]
        return input_enc

    dataset = Dataset.from_dict(dataset_dict)
    return dataset.map(tokenize)


# --- Fine-tune using PEFT (LoRA) ---
def fine_tune_peft(dataset, output_dir="./t5_lora_finetuned", epochs=3, model_name="./t5-small"):
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # LoRA config
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        task_type=TaskType.SEQ_2_SEQ_LM,
        lora_dropout=0.1,
        inference_mode=False
    )

    model = get_peft_model(model, lora_config)

    # Tokenize dataset
    tokenized_dataset = tokenize_dataset(dataset, tokenizer)

    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        num_train_epochs=epochs,
        logging_steps=10,
        save_steps=50,
        save_total_limit=2,
        remove_unused_columns=False,
        evaluation_strategy="no",
        fp16=torch.cuda.is_available(),  # Mixed precision if on GPU
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    trainer.train()

    # Save model and tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"✅ PEFT fine-tuned model saved to: {output_dir}")


# --- Main ---
if __name__ == "__main__":
    excel_file = "Template for report_new.xlsx"  # Change to your file path
    dataset_dict = prepare_dataset(excel_file, examples_per_sheet=30)

    fine_tune_peft(dataset_dict, output_dir="./t5_lora_finetuned", epochs=3)
