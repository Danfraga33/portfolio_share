from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import numpy as np
import pandas as pd

load_dotenv()
from .macro_compass import score

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vibrant-achievement-production.up.railway.app/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/macro-compass")
def get_macro_compass():
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise HTTPException(500, "FRED_API_KEY not set.")

    try:
        raw_df = score()
    except Exception as e:
        raise HTTPException(500, str(e))

    # ---- Convert DataFrame to Python types ----
    # 1) Cast everything to object so numpy types stay as numpy
    obj_df = raw_df.astype(object)

    # 2) Replace NaN / NA with None
    #    We use DataFrame.where to keep non-null values, else None:
    clean_df = obj_df.where(pd.notna(obj_df), None)

    # 3) Convert to dict-of-dicts (keyed by index)
    data = clean_df.to_dict(orient="index")

    # 4) jsonable_encoder will turn numpy.int64/float64 → int/float
    safe = jsonable_encoder(data)

    return JSONResponse(content=safe)
