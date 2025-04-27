import pytest, asyncio
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_create_post_successfully(async_client: AsyncClient):
    """Test creating a post successfully."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }

    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == payload["title"]


@pytest.mark.asyncio
async def test_create_post_missing_fields(async_client: AsyncClient):
    """Test validation errors when required fields are missing."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        # "content" is missing
        "user_id": "user-123"
    }
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "content" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_create_post_duplicate_slug(async_client: AsyncClient):
    """Test that creating a post with an existing slug fails."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]
    # Now try to create it again
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_post_by_slug(async_client: AsyncClient):
    """Test retrieving a single post by its slug."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]

    # Now try to get the post by slug
    response = await async_client.get(f"/posts/{payload['slug']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == payload["slug"]


@pytest.mark.asyncio
async def test_get_post_not_found(async_client: AsyncClient):
    """Test retrieving a post that does not exist."""
    response = await async_client.get("/posts/non-existent-slug")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Post does not exist"


@pytest.mark.asyncio
async def test_update_post_success(async_client: AsyncClient):
    """Test updating an existing post."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }

    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]

    # Now update the post
    update_payload = {
        "title": "My Updated Post",
        "content": "This is the updated content of my first post.",
        "slug": "my-first-post"
    }
    response = await async_client.put(f"/posts/{payload['slug']}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_payload["title"]


@pytest.mark.asyncio
async def test_update_post_slug_conflict(async_client: AsyncClient):
    """Test updating a post with a slug that already exists on another post."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]

    # Now create another post with the same slug
    conflicting_payload = {
        "title": "My Second Post",
        "slug": "my-first-post",  # Same slug as the first post
        "content": "This is the content of my second post.",
        "user_id": "user-456"
    }
    response = await async_client.post("/posts/", json=conflicting_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Slug already exists"


@pytest.mark.asyncio
async def test_update_post_not_found(async_client: AsyncClient):
    """Test updating a post that does not exist."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]
    # Now try to update a non-existent post
    update_payload = {
        "title": "My Updated Post",
        "content": "This is the updated content of my first post.",
        "slug": "non-existent-slug"
    }
    response = await async_client.put(f"/posts/non-existent-slug", json=update_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_post_success(async_client: AsyncClient):
    """Test deleting an existing post."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]
    # Now delete the post
    response = await async_client.delete(f"/posts/{payload['slug']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Post deleted successfully"


@pytest.mark.asyncio
async def test_delete_post_not_found(async_client: AsyncClient):
    """Test deleting a non-existent post."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == payload["slug"]
    # Now delete a non-existent post
    response = await async_client.delete("/posts/non-existent-slug")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Post does not exist"


@pytest.mark.asyncio
async def test_list_all_posts(async_client: AsyncClient):
    """Test listing all posts."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    payload_2 = {
        "title": "My Second Post",
        "slug": "my-second-post",
        "content": "This is the content of my second post.",
        "user_id": "user-456"
    }
    # Create another post
    response = await async_client.post("/posts/", json=payload_2)
    assert response.status_code == status.HTTP_201_CREATED

    # Now list all posts
    response = await async_client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK

    # Force parsing FULL body
    posts = response.json()
    assert isinstance(posts, list)

    # Force traversing the list
    titles = [post["title"] for post in posts]

    # Assert real content exists
    assert "My First Post" in titles
    assert "My Second Post" in titles
    assert len(posts) >= 2


@pytest.mark.asyncio
async def test_filter_posts_by_tag(async_client: AsyncClient):
    """Test filtering posts by a specific tag."""
    payload = {
        "title": "My First Post",
        "slug": "my-first-post",
        "content": "This is the content of my first post.",
        "user_id": "user-123"
    }
    # First create the post
    response = await async_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Now filter posts by a specific tag
    response = await async_client.get("/posts/?tag=my-tag")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)