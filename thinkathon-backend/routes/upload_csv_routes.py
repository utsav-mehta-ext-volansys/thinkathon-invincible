from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil
from your_script import read_file, read_ref_file, flag_out_of_range
from map_categories import map_columns_to_categories
from prepare_ml_data import prepare_data

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
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
        reference_sheets = read_ref_file("reference_excel.xlsx")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading reference file: {e}")

    # Map columns to categories
    column_names = df.columns.tolist()
    category_mapping = map_columns_to_categories(column_names)

    # Flag out-of-range values
    df = flag_out_of_range(df, reference_sheets, category_mapping)

    # Prepare ML data
    processed_df = prepare_data(df)

    # Convert to JSON-friendly format
    result = processed_df.to_dict(orient="records")
    return JSONResponse(content={"data": result})
