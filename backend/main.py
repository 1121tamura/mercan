from fastapi import FastAPI

from presentation.routers import health

app = FastAPI()

app.include_router(health.router)
