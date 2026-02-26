import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# ✅ Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_image(
    file: UploadFile,
    folder: str = "blogs",  # ✅ organize by folder
) -> str:
    # ✅ Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_IMAGE_TYPES}"
        )

    # ✅ Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB"
        )

    # ✅ Upload to Cloudinary
    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="image",
        transformation=[
            {"quality": "auto"},       # ✅ auto optimize quality
            {"fetch_format": "auto"},  # ✅ auto convert to webp if supported
        ]
    )

    return result["secure_url"]


async def upload_avatar(file: UploadFile) -> str:
    # ✅ Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")

    # ✅ Upload with avatar-specific transformations
    result = cloudinary.uploader.upload(
        contents,
        folder="blogs/avatars",
        resource_type="image",
        transformation=[
            {"width": 300, "height": 300, "crop": "fill", "gravity": "face"},  # ✅ crop to face
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ]
    )

    return result["secure_url"]


async def upload_thumbnail(file: UploadFile) -> str:
    # ✅ Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")

    # ✅ Upload with thumbnail-specific transformations
    result = cloudinary.uploader.upload(
        contents,
        folder="blogs/thumbnails",
        resource_type="image",
        transformation=[
            {"width": 1200, "height": 630, "crop": "fill"},  # ✅ OG image size
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ]
    )

    return result["secure_url"]


async def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)