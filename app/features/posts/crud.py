from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.features.posts.models import Post, PostTag
from app.features.tags.models import Tag
from app.features.roles.models import UserRole


async def get_all_posts(db: AsyncSession, published_only: bool = True) -> list[Post]:
    query = (
        select(Post)
        .options(
            joinedload(Post.user),
            joinedload(Post.category),
            joinedload(Post.tags).joinedload(PostTag.tag),  # 
        )
    )
    if published_only:
        query = query.where(Post.is_published == True)
    query = query.order_by(Post.created_at.desc())
    result = await db.execute(query)
    return result.unique().scalars().all()

async def get_post_by_id(db: AsyncSession, post_id: UUID) -> Post | None:
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(
            joinedload(Post.user),
            joinedload(Post.category),
            joinedload(Post.tags).joinedload(PostTag.tag),  # tags not post_tags
        )
    )
    return result.unique().scalar_one_or_none()

async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(
        select(Post)
        .where(Post.slug == slug)
        .options(
            joinedload(Post.user),
            joinedload(Post.category),
            joinedload(Post.tags).joinedload(PostTag.tag),  # 
        )
    )
    return result.unique().scalar_one_or_none()


async def get_user_posts(db: AsyncSession, user_id: UUID) -> list[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.user_id == user_id)
        .options(
            joinedload(Post.user),
            joinedload(Post.category),
            joinedload(Post.tags).joinedload(PostTag.tag),  # 
        )
        .order_by(Post.created_at.desc())
    )
    return result.unique().scalars().all()


async def create_post(db: AsyncSession, data: dict) -> Post:
    post = Post(**data)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(db: AsyncSession, post: Post, data: dict) -> Post:
    for key, value in data.items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post: Post) -> None:
    await db.delete(post)
    await db.commit()


# ─── Tags ─────────────────────────────────────────────────────────────────
async def get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    from app.features.tags.crud import generate_slug
    slug = generate_slug(name)
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
    return tag


async def sync_post_tags(db: AsyncSession, post: Post, tag_names: list[str]) -> None:
    # Delete existing post tags
    from sqlalchemy import delete
    await db.execute(delete(PostTag).where(PostTag.post_id == post.id))
    await db.commit()

    # Create new post tags
    for name in tag_names:
        tag = await get_or_create_tag(db, name)
        db.add(PostTag(post_id=post.id, tag_id=tag.id))

    await db.commit()


async def reload_post(db: AsyncSession, post_id: UUID) -> Post:
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(
            joinedload(Post.user),
            joinedload(Post.category),
            joinedload(Post.tags).joinedload(PostTag.tag),  # 
        )
    )
    return result.unique().scalar_one()