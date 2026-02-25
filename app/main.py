import uvicorn
from fastapi import FastAPI
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
import asyncio
from app.utilities.exceptions import AppException, app_exception_handler, unhandled_exception_handler
from app.core.seed import seed_roles_and_permissions, seed_admin_user
from fastapi.middleware.cors import CORSMiddleware

from app.features.users.routers import router as user_routers
from app.features.auth.routers import router as auth_routers
from app.features.roles.routers import router as role_routers
from app.features.categories.routers import router as category_routers
from app.features.tags.routers import router as tag_routers
from app.features.posts.routers import router as post_routers
from app.features.comments.routers import router as comment_routers

app = FastAPI(title="Learning Process ")

#  Exception handlers 
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include auth routes
app.include_router(auth_routers)
app.include_router(category_routers)
app.include_router(user_routers)
app.include_router(role_routers)
app.include_router(tag_routers)
app.include_router(post_routers)
app.include_router(comment_routers,prefix="/posts")


@app.get("/")
async def root():
    return {"message": "Hello World!!"}

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await seed_roles_and_permissions(db)

     # Create first admin (change email + password)
    async with AsyncSessionLocal() as db:
        await seed_admin_user(db, email="admin@blog.com", password="Admin@123")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)