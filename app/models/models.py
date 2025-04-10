from pydantic import BaseModel


class Tag(BaseModel):
    id: str
    name: str

class Post(BaseModel):
    id: str
    user_id: str
    title: str
    slug: str
    content: str

class PostTag(BaseModel):
    post_id: str
    tag_id: str

class PostVersion(BaseModel):
    id: str
    post_id: str
    version: int
    title: str
    content: str
    created_at: str

class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: str