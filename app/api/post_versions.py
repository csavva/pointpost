from fastapi import APIRouter


router = APIRouter()

@router.get("/posts/{slug}/versions", tags=["Post Versions"])
def get_posts_versions(slug: str):
    #TODO: Implement logic to get all versions of a specific post
    pass

@router.post("/posts/{slug}/restore/{version_id}", tags=["Post Versions"])
def restore_post(slug: str, version_id: int):
    #TODO: Implement logic to restore a specific version of a post
    pass
