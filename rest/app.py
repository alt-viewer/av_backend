from fastapi import FastAPI

from rest.routers import routers

app = FastAPI()

# Routers here
for router in routers:
    app.include_router(router)
