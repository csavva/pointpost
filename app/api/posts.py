import uuid

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.postgres import get_db
from app.models.models import PostCreate, PostRead, PostUpdate
from app.models.sql import Post

router = APIRouter()

@router.post("/posts/", tags=["Posts"], response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(post : PostCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a new blog post. This function handles the creation of a post provided by the user
    and stores it in the database. It ensures that the slug for the post is unique. If the slug
    already exists, an HTTP exception is raised. After successful creation, the function
    returns the newly created post.

    :param post: The PostCreate object containing the details for the post to be created.
    :type post: PostCreate
    :param db: The asynchronous database session dependency to interact with the database.
    :type db: AsyncSession
    :return: The newly created post as a PostRead object.
    :rtype: PostRead
    :raises HTTPException: If the slug provided for the post already exists in the database.
    """

    # Check if the slug is unique
    result = await db.execute(select(Post).where(Post.slug == post.slug))
    existing_post = result.scalar_one_or_none()
    if existing_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    # Create a new post
    new_post = Post(
        id=str(uuid.uuid4()),
        title=post.title,
        content=post.content,
        user_id=post.user_id,
        slug=post.slug
    )

    # Add the new post to the database
    db.add(new_post)
    await  db.commit()
    await db.refresh(new_post)

    return new_post

@router.put("/posts/{slug}", tags=["Posts"], response_model=PostRead, status_code=status.HTTP_200_OK)
async def update_post(slug: str, post: PostUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update an existing post based on the given slug. Validates the uniqueness of the slug and performs
    an update in the database if the post exists. If the post with the specified slug does not exist or
    the new slug is already in use, an appropriate HTTP exception is raised.

    :param slug: The unique identifier for the post that needs to be updated
    :type slug: str
    :param post: The data containing the updated post details
    :type post: PostUpdate
    :param db: The database session dependency for interacting with the database
    :type db: AsyncSession
    :return: The updated post object after successful modification and saving to the database
    :rtype: PostRead
    :raises HTTPException: If the post with the specified slug does not exist or if the new slug is
                           already in use by another post
    """

    # Check if the post exists in order to update it
    result = await db.execute(select(Post).where(Post.slug == slug))
    existing_post = result.scalar_one_or_none()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slug does not exist")

    # Check if the new slug is unique
    result = await db.execute(select(Post).where(Post.slug == post.slug))
    existing_slug_post = result.scalar_one_or_none()
    if existing_slug_post and existing_slug_post.id != existing_post.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    # Update the post
    existing_post.title = post.title
    existing_post.content = post.content
    existing_post.slug = post.slug

    # Commit the changes to the database
    db.add(existing_post)
    await db.commit()
    await db.refresh(existing_post)

    return existing_post

@router.get("/posts/", tags=["Posts"])
async def list_posts(db: AsyncSession = Depends(get_db)):
    """
    Fetches and returns a list of all posts from the database.

    This function queries the database to retrieve all available posts. It
    executes a SELECT statement on the `Post` table, collects the results, and
    returns the posts in the response.

    :param db: The database session dependency used for executing the query.
    :type db: AsyncSession
    :return: A list of all posts retrieved from the database.
    :rtype: list
    """

    # Fetch all posts from the database
    result = await db.execute(select(Post))
    posts = result.scalars().all()

    return posts

@router.get("/posts/{slug}", tags=["Posts"], response_model=PostRead, status_code=status.HTTP_200_OK)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch a post by its unique slug from the database.

    This endpoint retrieves a specific post based on the slug provided in the
    request. The slug is a unique identifier for each post in the database.
    If no post with the provided slug is found, an HTTP exception is raised.

    :param slug: The unique identifier for the post, provided as a string
                 in the URL path.
    :type slug: str
    :param db: An asynchronous database session object used for querying
               the post.
    :type db: AsyncSession
    :return: The post corresponding to the given slug if it exists in
             the database.
    :rtype: Post
    :raises HTTPException: If the slug does not correspond to an existing
                           post, raises an HTTP 400 exception.
    """

    # Check if the post exists
    result = await db.execute(select(Post).where(Post.slug == slug))
    existing_post = result.scalar_one_or_none()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")

    return existing_post


@router.delete("/posts/{slug}", tags=["Posts"])
async def delete_post(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Deletes a post with the specified slug from the database.

    This function handles the deletion of a post identified by its slug. It first
    checks the existence of the post based on the provided slug. If the post exists,
    it proceeds to delete the record and commits the changes to the database. If
    the specified slug does not correspond to any existing post, an HTTP exception
    is raised indicating the error.

    :param slug: The unique identifier (slug) of the post to be deleted.
    :type slug: str
    :param db: The database session used to perform database queries and
               operations.
    :type db: AsyncSession
    :return: A dictionary containing a success message after the post
             has been deleted.
    :rtype: dict
    :raises HTTPException: If the provided slug does not correspond to any
                           existing post in the database.
    """

    # Check if the post exists in order to delete it
    result = await db.execute(select(Post).where(Post.slug == slug))
    existing_post = result.scalar_one_or_none()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")

    # Delete the post
    await db.delete(existing_post)
    await db.commit()

    return {
        "detail": "Post deleted successfully"
    }