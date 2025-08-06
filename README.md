Project README

Prerequisite

- Make sure to have the Google T5-small model downloaded and available locally before running any scripts.
  - You can download the model from https://huggingface.co/google/t5-small
  - Place the model files in an accessible directory on your system.

---

Backend Setup

1. Install backend dependencies:
   pip install -r requirement.txt

2. Run the backend server:
   uvicorn main:app --reload

The backend will start running locally with hot reload enabled.

---

Model Fine-tuning

To generate the recommendation model using the fine-tuning script, run:

   python mode_peft_finetuned.py

This script will use the local Google T5-small model and produce the recommendation model output.

---

Frontend Setup

1. Install frontend dependencies:
   npm install

2. Run the frontend development server:
   npm run dev

The frontend will be available locally with hot reload enabled for development.

---

Summary

Component          | Command                              | Notes
-------------------|--------------------------------------|----------------------------------------
Google T5-small    | Download manually                    | Required locally before running scripts.
Backend            | pip install -r requirement.txt       | Starts backend API server.
Model Fine-tune    | python mode_peft_finetuned.py        | Generates the recommendation model.
Frontend           | npm install                          | Starts frontend development server.
---

Additional Notes

- Ensure your environment has Python and Node.js installed.
- Adjust any file paths or environment variables as needed for your setup.
- If you encounter issues with model loading, verify the model path and availability.

---

Feel free to contribute or report issues!
