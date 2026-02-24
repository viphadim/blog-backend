import uvicorn
from fastapi import FastAPI
from app.db.session import engine, Base
from app.db.base import Base
import asyncio
from app.features.users.routers import router as user_routers
from app.features.auth.routers import router as auth_routers

app = FastAPI(title="Blogs ")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    

# Include auth routes
app.include_router(auth_routers)
app.include_router(user_routers)

@app.get("/")
async def root():
    return {"message": "Hello World!!"}

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)