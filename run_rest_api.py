import uvicorn

from rest import app as AppModule

if __name__ == "__main__":
    uvicorn.run(AppModule.app, host="127.0.0.1", port=4482)
