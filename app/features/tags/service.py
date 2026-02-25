from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import re

from app.features.tags import crud
from app.features.tags.models import Tag
from app.features.tags.schemas import CreateTagRequest, UpdateTagRequest
from app.utilities.exceptions import NotFoundException, ConflictException


def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug


async def get_all_tags(db: AsyncSession) -> list[Tag]:
    return await crud.get_all_tags(db)


async def get_tag_by_id(db: AsyncSession, tag_id: UUID) -> Tag:
    tag = await crud.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundException("Tag not found")
    return tag


async def create_tag(db: AsyncSession, data: CreateTagRequest) -> Tag:
    slug = generate_slug(data.name)
    existing = await crud.get_tag_by_slug(db, slug)
    if existing:
        raise ConflictException("Tag already exists")

    return await crud.create_tag(db, {
        "name": data.name,
        "slug": slug,
    })


async def update_tag(db: AsyncSession, tag_id: UUID, data: UpdateTagRequest) -> Tag:
    tag = await crud.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundException("Tag not found")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        slug = generate_slug(update_data["name"])
        existing = await crud.get_tag_by_slug(db, slug)
        if existing and existing.id != tag_id:
            raise ConflictException("Tag name already exists")
        update_data["slug"] = slug

    return await crud.update_tag(db, tag, update_data)


async def delete_tag(db: AsyncSession, tag_id: UUID) -> None:
    tag = await crud.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundException("Tag not found")
    await crud.delete_tag(db, tag)