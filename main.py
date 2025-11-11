import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import create_document
from schemas import Booking

app = FastAPI(title="L&M CAR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "L&M CAR API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Connected"
            response["collections"] = db.list_collection_names()
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

class BookingResponse(BaseModel):
    id: str
    message: str

@app.post("/book", response_model=BookingResponse)
async def create_booking(booking: Booking):
    # Basic validation: ensure dates make sense
    if booking.return_date <= booking.pickup_date:
        raise HTTPException(status_code=400, detail="Return date must be after pickup date")

    inserted_id = create_document("booking", booking)
    return {"id": inserted_id, "message": "Booking received. We will confirm shortly."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
