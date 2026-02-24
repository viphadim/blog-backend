from app.db.base import Base
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_deleted = Column(Boolean, default=False)

    # users = relationship(
    #     "User",
    #     secondary="user_roles",
    #     back_populates="roles"
    # )