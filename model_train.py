import pandas as pd
import random
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, AutoTokenizer, AutoModelForSeq2SeqLM
import datasets

# --- Step 1: Load ranges from Excel ---
def load_ranges_from_excel(file_path):
    xls = pd.ExcelFile(file_path)
    all_ranges = {}

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        df.columns = [col.strip() for col in df.columns]
        print("df.columns",df.columns)
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
            low = row['Low']
            high = row['High']
            unit = row['Unit'] if not pd.isna(row['Unit']) else ""
            param_dict[param] = (low, high, unit)
        all_ranges[sheet] = param_dict

    return all_ranges


# --- Step 2: Generate synthetic examples ---
def generate_synthetic_examples(param_dict, sheet_name, num_examples=20):
    params = list(param_dict.keys())
    examples = []

    for _ in range(num_examples):
        input_parts = []
        abnormalities = []
        for param in params:
            low, high, unit = param_dict[param]

            # 70% normal, 30% abnormal (randomly low or high)
            if random.random() < 0.7:
                if pd.isna(low) or pd.isna(high):
                    val = random.randint(1, 100)
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

            # Compose input string
            unit_str = f" {unit}" if unit else ""
            input_parts.append(f"{param}: {val}")

            if status != 'normal':
                abnormalities.append((param, status))

        # Generate human-friendly summary
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


# --- Step 3: Prepare dataset ---
def prepare_dataset(file_path, examples_per_sheet=20):
    all_ranges = load_ranges_from_excel(file_path)
    dataset = {"input_text": [], "target_text": []}

    for sheet, param_dict in all_ranges.items():
        print(f"Generating data for sheet: {sheet} ({len(param_dict)} params)")
        examples = generate_synthetic_examples(param_dict, sheet, examples_per_sheet)
        print("examples",examples)
        for inp, tgt in examples:
            dataset["input_text"].append(inp)
            print("input_text",inp)
            dataset["target_text"].append(tgt)
            print("output_text",tgt)

    return dataset


# --- Step 4: Preprocess for T5 ---
def preprocess_for_t5(tokenizer, dataset, max_len=128):
    def preprocess_function(examples):
        inputs = tokenizer(examples["input_text"], truncation=True, padding="max_length", max_length=max_len)
        targets = tokenizer(examples["target_text"], truncation=True, padding="max_length", max_length=max_len)
        inputs["labels"] = targets["input_ids"]
        return inputs

    ds = datasets.Dataset.from_dict(dataset)
    tokenized_ds = ds.map(preprocess_function, batched=True)
    return tokenized_ds


# --- Step 5: Fine-tune model ---
def fine_tune_t5(tokenized_ds, output_dir="./t5_finetuned", epochs=3):
    model_name = "google-t5/t5-small"
    tokenizer = AutoTokenizer.from_pretrained('./t5-small',local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained('./t5-small',local_files_only=True)
    # tokenizer = T5Tokenizer.from_pretrained(model_name,token="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")
    # model = T5ForConditionalGeneration.from_pretrained(model_name,token="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")

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        num_train_epochs=epochs,
        logging_steps=10,
        save_steps=50,
        evaluation_strategy="no",
        save_total_limit=2,
        remove_unused_columns=True,
        push_to_hub=False,
        seed=42,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds,
    )

    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model fine-tuned and saved to {output_dir}")


# --- Main execution ---
if __name__ == "__main__":
    excel_file = "Template for report_new.xlsx"  # your Excel path here
    print("Preparing dataset from Excel...")
    dataset = prepare_dataset(excel_file, examples_per_sheet=30)

    print("Loading tokenizer...")
    tokenizer = T5Tokenizer.from_pretrained("t5-small")

    print("Preprocessing dataset for T5...")
    tokenized_dataset = preprocess_for_t5(tokenizer, dataset)

    print("Fine-tuning T5 model...")
    fine_tune_t5(tokenized_dataset, output_dir="./t5_finetuned", epochs=3)

    print("All done! Your fine-tuned model is ready.")
