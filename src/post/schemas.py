from datetime import datetime
from pydantic import BaseModel


class CommentBaseModel(BaseModel):
    comment_content: str


class CommentInModel(CommentBaseModel):
    user_id: int
    post_id: int


class CommentOutModel(CommentInModel):
    comment_id: int
    commented_at: datetime

    class ConfigDict:
        from_attributes = True


class PostBaseModel(BaseModel):
    post_title: str
    post_content: str
    post_image: str | None = None


class PostInModel(PostBaseModel):
    user_id: int


class PostOutModel(PostBaseModel):
    post_id: int
    user_id: int
    posted_at: datetime
    total_likes: int
    total_dislikes: int
    total_comments: int
    hashtags: list[str]
    comments: list
    liked_by: list
    disliked_by: list

    class ConfigDict:
        from_attributes = True


class PostUpdateModel(BaseModel):
    post_title: str | None
    post_content: str | None
    post_image: str | None = None


class DeleteOutModel(BaseModel):
    message: str
    post: PostOutModel | None = None
