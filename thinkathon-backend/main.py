# pylint: disable=import-error
"""Main File"""
from fastapi import FastAPI
from routes.auth_routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router, prefix="/api/auth")

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)
@app.get("/")
async def home():
    """Home Page Endpoint"""
    return {"message": "Hello World"}
