from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint

from app.db import Base


class User(Base):

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )

    id = Column(Integer, primary_key=True)

    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)

    email = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
