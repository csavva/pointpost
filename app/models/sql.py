from sqlalchemy import Column, String, Boolean
from app.db.postgres import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)

class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(String, primary_key=True, index=True)
    tag_id = Column(String, primary_key=True, index=True)

class PostVersion(Base):
    __tablename__ = "post_versions"

    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, nullable=False)
    version = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(String, nullable=False)