from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!!"}


@app.get("/test")
async def testing(first_name:str,last_name:str):
    full_name = first_name.title() + " " + last_name.title()
    return {"full_name":full_name }
