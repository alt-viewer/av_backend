import uvicorn
from dotenv import load_dotenv

from rest import app as AppModule

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(AppModule.app, host="127.0.0.1", port=4482)
