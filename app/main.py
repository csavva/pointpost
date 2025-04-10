import uvicorn
import os
import dotenv
from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.post_versions import router as post_versions_router
from app.api.tags import router as tags_router
from app.api.rss import router as rss_router


dotenv.load_dotenv()

app = FastAPI()


app.include_router(auth_router)

app.include_router(post_versions_router)

app.include_router(tags_router)

app.include_router(posts_router)

app.include_router(rss_router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("PORT", 8080)))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
