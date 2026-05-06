from fastapi import FastAPI
from typing import Dict
from .routes.research import router as research_router
from .routes.signup import router as signup_router


app = FastAPI()

app.include_router(research_router, prefix='/api/v1')
app.include_router(signup_router, prefix='/api/v1')


@app.get("/health")
async def health_check() -> Dict:
    return {"status": "ok"}
