import uvicorn
from fastapi import FastAPI
from app.db.session import engine, Base
from app.db.base import Base
import asyncio
from app.features.users.routers import router as user_route

app = FastAPI(title="Blogs API")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    
@app.get("/")
async def root():
    return {"message": "Hello World!!"}


@app.get("/test")
async def testing(first_name:str,last_name:str):
    full_name = first_name.title() + " " + last_name.title()
    return {"full_name":full_name }

# Include auth routes
app.include_router(user_route)

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)