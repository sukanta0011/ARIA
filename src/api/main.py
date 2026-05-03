from fastapi import FastAPI
from typing import Dict


app = FastAPI()


@app.get("/health")
async def health_check() -> Dict:
    return {"status": "ok"}
