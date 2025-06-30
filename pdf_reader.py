import pandas as pd
import os
import pdfplumber


def read_pdf_file(file_path):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            print(page.extract_text())
            print(page.extract_tables())

def main():
    import os

    file_path = input("Enter path to your pdf file: ").strip()

    if not os.path.exists(file_path):
        print("File not found.")
        return

    try:
        df = read_pdf_file(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

if __name__ == "__main__":
    main()
