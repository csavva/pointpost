import uvicorn
import os
import dotenv
from fastapi import FastAPI

dotenv.load_dotenv()

app = FastAPI()

@app.post("/auth/register", tags=["auth"])
def register():
    #TODO: Implement registration logic
    pass

@app.post("/auth/login", tags=["auth"])
def login():
    #TODO: Implement login logic
    pass

@app.get("/users/me", tags=["auth"])
def get_current_user():
    #TODO: Implement logic to get current user
    pass

@app.post("/posts/", tags=["posts"])
def create_post():
    #TODO: Implement logic to create a new post
    pass

@app.get("/posts/", tags=["posts"])
def list_posts():
    #TODO: Implement logic to list all posts
    pass

@app.get("/posts/{slug}", tags=["posts"])
def get_post(slug: str):
    #TODO: Implement logic to get a specific post
    pass

@app.put("/posts/{slug}", tags=["posts"])
def update_post(slug: str):
    #TODO: Implement logic to update a specific post
    pass

@app.delete("/posts/{slug}", tags=["posts"])
def delete_post(slug: str):
    #TODO: Implement logic to delete a specific post
    pass

@app.get("/tags/", tags=["tags"])
def get_tags():
    #TODO: Implement logic to get all tags
    pass

@app.post("/posts/{slug}/tags", tags=["tags", "posts"])
def add_post_tags(slug: str):
    #TODO: Implement logic to add tags to a specific post
    pass


@app.get("/posts/{slug}/versions", tags=["posts", "versions"])
def get_posts_versions(slug: str):
    #TODO: Implement logic to get all versions of a specific post
    pass

@app.post("/posts/{slug}/restore/{version_id}", tags=["posts", "versions"])
def restore_post(slug: str, version_id: int):
    #TODO: Implement logic to restore a specific version of a post
    pass

@app.get("/rss.xml", tags=["rss"])
def get_rss():
    #TODO: Implement logic to get RSS feed
    pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("PORT", 8080)))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
