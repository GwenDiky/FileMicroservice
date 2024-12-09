import uvicorn
from fastapi import FastAPI
from src.core.consumer import start_listen

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await start_listen()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8085)
