from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.features.categories.models import Category
from sqlalchemy.future import select
from uuid import UUID


async def get_all_categories(db:AsyncSession)->List[Category]:
    qurrey=await db.execute(select(Category).order_by(Category.name))
    return qurrey.scalars().all()


async def create_category(db: AsyncSession, data: dict) -> Category:
    category=Category(**data)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db:AsyncSession, category: Category, data: dict) ->Category:
    for key, value in data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def get_category_by_id(db:AsyncSession,category_id:UUID) ->Category:
    qurrey= await db.execute(select(Category).where(Category.id==category_id))
    result= qurrey.scalar_one_or_none()
    return result

async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()


async def delete_category(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()