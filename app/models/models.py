from pydantic import BaseModel

# =========================
# Tag model

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    id: str

class TagRead(TagBase):
    id: str

    class Config:
        orm_mode = True

class Tag(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

# =========================
# Post model

class PostBase(BaseModel):
    title: str
    slug: str
    content: str

class PostCreate(PostBase):
    user_id: str

class PostUpdate(PostBase):
    pass

class PostRead(PostBase):
    id: str

    class Config:
        orm_mode = True

# =========================
# PostTag model

class PostTagBase(BaseModel):
    post_id: str
    tag_id: str

class PostTagCreate(PostTagBase):
    pass

# =========================
# PostVersion model

class PostVersionBase(BaseModel):
    post_id: str
    version: int
    title: str
    content: str

class PostVersionCreate(PostVersionBase):
    pass

class PostVersionRead(PostVersionBase):
    id: str
    version: int
    title: str
    created_at: str

    class Config:
        orm_mode = True

# =========================
# User model

class UserBase(BaseModel):
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: str

class UserRead(UserBase):
    id: str
    created_at: str

    class Config:
        orm_mode = True
