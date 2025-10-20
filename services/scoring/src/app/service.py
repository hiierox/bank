from fastapi import FastAPI

from app.api.scoring.handler import router as scoring_router

app = FastAPI()

app.include_router(scoring_router, prefix='/api/scoring')
