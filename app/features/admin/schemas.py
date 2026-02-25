from pydantic import BaseModel
from datetime import datetime

class DashboardStatsResponse(BaseModel):
    total_users: int
    total_posts: int
    total_published_posts: int
    total_unpublished_posts: int
    total_comments: int
    total_likes: int
    total_bookmarks: int
    new_users_today: int
    new_posts_today: int


class AssignRoleRequest(BaseModel):
    role_name: str  # "admin", "editor", "author", "reader"


class MessageResponse(BaseModel):
    message: str