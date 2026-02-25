from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import re

from app.features.posts import crud
from app.features.posts.models import Post
from app.features.posts.schemas import CreatePostRequest, UpdatePostRequest
from app.features.users.models import User
from app.features.users import crud as user_crud
from app.features.roles import crud as role_crud
from app.utilities.exceptions import NotFoundException, ForbiddenException, ConflictException


def generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug


async def get_all_posts1(db: AsyncSession) -> list[Post]:
    return await crud.get_all_posts(db, published_only=True)

    
async def get_all_posts(db: AsyncSession, current_user=None) -> list[Post]:
    user_role_names = []
    if current_user:
        user_role_names = [ur.role.name for ur in current_user.user_roles]

    #   Admin/editor sees all posts including unpublished
    if any(r in user_role_names for r in ["admin"]):
        return await crud.get_all_posts(db, published_only=False)

    #  Everyone else sees published only
    return await crud.get_all_posts(db, published_only=True)

async def get_my_posts(db: AsyncSession, user_id: UUID) -> list[Post]:
    return await crud.get_user_posts(db, user_id)


async def get_post(db: AsyncSession, post_id: UUID) -> Post:
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")
    return post


async def create_post(db: AsyncSession, user: User, data: CreatePostRequest) -> Post:
    #  Generate unique slug
    slug = generate_slug(data.title)
    existing = await crud.get_post_by_slug(db, slug)
    if existing:
        raise ConflictException("Post with this title already exists")

    post = await crud.create_post(db, {
        "title": data.title,
        "slug": slug,
        "content": data.content,
        "thumbnail": data.thumbnail,
        "category_id": data.category_id,
        "user_id": user.id,
        "is_published": False,
    })

    #  Sync tags — auto create if not exist
    if data.tags:
        await crud.sync_post_tags(db, post, data.tags)

    #  Auto promote reader → author on first post
    user_role_names = [ur.role.name for ur in user.user_roles]
    if "reader" in user_role_names and "author" not in user_role_names:
        author_role = await role_crud.get_role_by_name(db, "author")
        if author_role:
            await role_crud.assign_role_to_user(db, user.id, author_role.id)

    #  Reload post with all relationships
    return await crud.reload_post(db, post.id)


async def update_post(db: AsyncSession, user: User, post_id: UUID, data: UpdatePostRequest) -> Post:
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")

    user_role_names = [ur.role.name for ur in user.user_roles]

    #  Only owner, editor, or admin can update
    if post.user_id != user.id and not any(r in user_role_names for r in ["editor","author", "admin"]):
        raise ForbiddenException("You can only update your own posts")

    update_data = data.model_dump(exclude_unset=True, exclude={"tags"})

    #  Regenerate slug if title changed
    if "title" in update_data:
        slug = generate_slug(update_data["title"])
        existing = await crud.get_post_by_slug(db, slug)
        if existing and existing.id != post_id:
            raise ConflictException("Post with this title already exists")
        update_data["slug"] = slug

    await crud.update_post(db, post, update_data)

    #  Sync tags if provided
    if data.tags is not None:
        await crud.sync_post_tags(db, post, data.tags)

    return await crud.reload_post(db, post.id)


async def publish_post(db: AsyncSession, user: User, post_id: UUID) -> Post:
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")

    user_role_names = [ur.role.name for ur in user.user_roles]
    if not any(r in user_role_names for r in ["editor","author", "admin"]):
        raise ForbiddenException("Only editors and admins can publish posts")

    await crud.update_post(db, post, {"is_published": True})
    return await crud.reload_post(db, post.id)


async def unpublish_post(db: AsyncSession, user: User, post_id: UUID) -> Post:
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")

    user_role_names = [ur.role.name for ur in user.user_roles]
    if not any(r in user_role_names for r in ["editor","author", "admin"]):
        raise ForbiddenException("Only editors and admins can unpublish posts")

    await crud.update_post(db, post, {"is_published": False})
    return await crud.reload_post(db, post.id)


async def delete_post(db: AsyncSession, user: User, post_id: UUID) -> None:
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise NotFoundException("Post not found")

    user_role_names = [ur.role.name for ur in user.user_roles]
    if post.user_id != user.id and "admin" not in user_role_names:
        raise ForbiddenException("You can only delete your own posts")

    await crud.delete_post(db, post)