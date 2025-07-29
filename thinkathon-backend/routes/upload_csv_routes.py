from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil
import sys
base_dir = os.path.expanduser("~/Utsav's/Thinkathon/Code/thinkathon-invincible")
file_path = os.path.join(base_dir, "reference_excel.xlsx")
scripts_path = os.path.join(base_dir, "scripts")
sys.path.append(scripts_path)
from cleanup_script import read_file, read_ref_file, flag_out_of_range
from map_categories import map_columns_to_categories
from prepare_ml_data import prepare_data

upload_router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = os.path.join(UPLOAD_DIR, file.filename)

    # Save file to disk
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read the uploaded file
    try:
        df = read_file(filename)
        if isinstance(df, str):
            raise HTTPException(status_code=400, detail="PDF file returned text. Please upload a CSV or Excel file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading uploaded file: {e}")

    # Read reference Excel
    try:
        reference_sheets = read_ref_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading reference file: {e}")

    print(df)
    # Map columns to categories
    column_names = df.columns.tolist()
    category_mapping = map_columns_to_categories(column_names)

    # Flag out-of-range values
    df = flag_out_of_range(df, reference_sheets, category_mapping)
    
    excluded_cols = ['Name', 'Age', 'ReportDate']
    excluded_data = df[excluded_cols] if all(col in df.columns for col in excluded_cols) else pd.DataFrame()
    
    df = df.drop(columns=[col for col in excluded_cols if col in df.columns])

    processed_data = prepare_data(df)
    user_data = excluded_data.to_dict(orient="records")
    user_info = user_data[0]

    # processed_data is a dict with 'tests' key
    final_output = {**user_info, **processed_data}

    # final_output now contains Name, Age, ReportDate plus tests key
    print(final_output)
    # if not excluded_data.empty:
    #     processed_df = pd.concat([excluded_data.reset_index(drop=True), processed_df.reset_index(drop=True)], axis=1)
    # # Convert to JSON-friendly format
    # result = processed_df.to_dict(orient="records")
    return JSONResponse(content={"data": final_output})
