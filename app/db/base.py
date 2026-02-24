# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

from app.db.session import Base

# Import all models here so Alembic can detect them
from app.features.users.models import User
from app.features.roles.models import Role, Permission, RolePermission, UserRole
from app.features.oauth.models import OAuthAccount
from app.features.categories.models import Category
from app.features.tags.models import Tag
from app.features.posts.models import Post, PostTag
from app.features.comments.models import Comment
from app.features.likes.models import Like
from app.features.bookmarks.models import Bookmark