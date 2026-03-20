from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def index():
    message={"message":"Service is Running"}
    return message