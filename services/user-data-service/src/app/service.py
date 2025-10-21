from fastapi import FastAPI

from app.api.user_data.handler import router as user_data_router

app = FastAPI()

app.include_router(user_data_router)
