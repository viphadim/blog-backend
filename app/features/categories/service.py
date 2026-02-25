from sqlalchemy.ext.asyncio import AsyncSession
from app.features.categories.models import Category
from app.features.categories import crud as cat_crud
import re

from app.utilities.exceptions import ConflictException,NotFoundException
from uuid import UUID
from app.features.categories.schemas import CreateCategoryRequest, UpdateCategoryRequest

def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug


async def get_all_categories(db: AsyncSession) -> list[Category]:
    return await cat_crud.get_all_categories(db)

async def get_category_by_id(db:AsyncSession,cate_id:UUID) ->Category:
    category=await cat_crud.get_category_by_id(db,cate_id)
    if not category:
        raise NotFoundException("Category not found")

    return category

async def create_category(db:AsyncSession,data:CreateCategoryRequest) ->Category:
    slug = generate_slug(data.name)

    existing = await cat_crud.get_category_by_slug(db, slug)
    if existing:
        raise ConflictException("Category already exists")

    return await cat_crud.create_category(db, {
        "name": data.name,
        "slug": slug,
        "description": data.description,
    })

async def update_category(db:AsyncSession,cate_id:UUID,data:UpdateCategoryRequest)->Category:
    category = await cat_crud.get_category_by_id(db, cate_id)
    if not category:
        raise NotFoundException("Category not found")
    
    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        slug=generate_slug(update_data["name"])
        existing=await cat_crud.get_category_by_slug(db,slug)
        if existing and existing.id != cate_id:
            raise ConflictException("Category name already exists")
        update_data["slug"] = slug

    return await cat_crud.update_category(db, category, update_data)

async def delete_category(db: AsyncSession, category_id: UUID) -> None:
    category = await cat_crud.get_category_by_id(db, category_id)
    if not category:
        raise NotFoundException("Category not found")
    await cat_crud.delete_category(db, category)