from fastapi import APIRouter


router = APIRouter()

@router.get("/tags/", tags=["Tags"])
def get_tags():
    #TODO: Implement logic to get all tags
    pass

@router.post("/posts/{slug}/tags", tags=["Tags"])
def add_post_tags(slug: str):
    #TODO: Implement logic to add tags to a specific post
    pass