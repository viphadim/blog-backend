from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.features.tags.models import Tag


import re

def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

async def get_all_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


async def get_tag_by_id(db: AsyncSession, tag_id: UUID) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_tag_by_slug(db: AsyncSession, slug: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, data: dict) -> Tag:
    tag = Tag(**data)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update_tag(db: AsyncSession, tag: Tag, data: dict) -> Tag:
    for key, value in data.items():
        setattr(tag, key, value)
    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag: Tag) -> None:
    await db.delete(tag)
    await db.commit()