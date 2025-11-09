from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from ..error import ItemNotFoundException, OperationNotAllowedException
from ..authentication.dependencies import get_current_user
from ..authentication.schemas import Payload
from ..db.database import get_session
from . import schemas, utils
from ..processor_image import delete_image, upload_image
from ..settings.config import config


post_router = APIRouter(prefix="/api/posts", tags=["post"])


@post_router.post("/", response_model=schemas.PostOutModel, status_code=201)
async def make_a_post(
    post_title: str = Form(None, examples=["My First Trip to Lagos"]),
    post_content: str = Form(None, examples=["I am about to share..."]),
    post_image: UploadFile | None = File(None),
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if post_image:
        image_url = await upload_image(post_image, config.POST_IMAGE_FOLDER, session)
    else:
        image_url = None
    add_post = schemas.PostInModel(
        post_title=post_title,
        post_content=post_content,
        post_image=image_url,
        user_id=current_user.user_id,
    )
    post = utils.create_new_post(post=add_post, session=session)
    return post


@post_router.get("/users/", response_model=list[schemas.PostOutModel])
def get_user_posts(
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_posts = utils.get_all_user_posts(session, current_user.user_id)
    return user_posts


@post_router.get("/{post_id}/", response_model=schemas.PostOutModel)
def get_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.get_post_by_id(post_id=post_id, session=session)
    return post


@post_router.get("/", response_model=list[schemas.PostOutModel])
def get_all_posts_in_db(session: Session = Depends(get_session)):
    posts = utils.get_all_posts(session=session)
    return posts


@post_router.put("/{post_id}/", response_model=schemas.PostOutModel, status_code=201)
async def update_post(
    post_id: int,
    post_title: str | None = Form(None, examples=["My First Trip to Lagos"]),
    post_content: str | None = Form(None, examples=["I am about to share..."]),
    post_image: UploadFile | None = File(None),
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.get_post_by_id(post_id, session, return_pydantic=False)
    if not post:
        raise ItemNotFoundException(f"Post with id {post_id} not found")
    if post.user_id != current_user.user_id:
        raise OperationNotAllowedException(
            "You are not allowed to make an edit to this post."
        )
    if post_image:
        folder_name = config.POST_IMAGE_FOLDER
        image_url = await upload_image(post_image, folder_name, session)
        if post.post_image:
            delete_image(post.post_image, session)
    else:
        image_url = post.post_image
    updated_post = schemas.PostUpdateModel(
        post_title=post_title, post_content=post_content, post_image=image_url
    )
    post_updated = utils.update_post(post_id, updated_post, session)
    return post_updated


@post_router.delete("/{post_id}/", response_model=schemas.DeleteOutModel)
def delete_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    utils.delete_post(post_id, current_user.user_id, session)
    return {"message": f"Post {post_id} deleted successfully"}


@post_router.get("/hashtags/{hashtag}", response_model=list[schemas.PostOutModel])
def get_posts_by_hashtags(
    hashtag: str,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    hashtag = hashtag.replace("#", "").lower().strip()
    posts = utils.get_posts_by_hashtags(hashtag=hashtag, session=session)
    return posts


@post_router.post("/{post_id}/comments/", status_code=201)
def add_comment_to_post(
    post_id: int,
    comment: schemas.CommentBaseModel,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    add_comment = schemas.CommentInModel(
        **comment.model_dump(), user_id=current_user.user_id, post_id=post_id
    )
    post = utils.add_comment_to_post(comment=add_comment, session=session)
    return post


@post_router.put(
    "/comments/{comment_id}/", response_model=schemas.CommentOutModel, status_code=201
)
def update_comment(
    comment_id: int,
    new_comment: schemas.CommentBaseModel,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    comment_updated = utils.edit_comment(
        comment_id, current_user.user_id, new_comment, session
    )
    return comment_updated


@post_router.delete("/comments/{comment_id}/", response_model=schemas.DeleteOutModel)
def delete_comment(
    comment_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    utils.delete_comment(comment_id, current_user.user_id, session)
    return {"message": f"Comment {comment_id} deleted successfully"}


@post_router.post(
    "/{post_id}/like/", response_model=schemas.PostOutModel, status_code=201
)
def like_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.like_post(post_id, current_user.user_id, session)
    return post


@post_router.delete("/{post_id}/like/", response_model=schemas.DeleteOutModel)
def remove_like_from_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.remove_like(post_id, current_user.user_id, session)
    return {"message": "unliked successful", "post": post}


@post_router.post(
    "/{post_id}/dislike/", response_model=schemas.DeleteOutModel, status_code=201
)
def dislike_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.dislike_post(post_id, current_user.user_id, session)
    return {"message": "undislike successful", "post": post}


@post_router.delete(
    "/{post_id}/dislike/", response_model=schemas.PostOutModel, status_code=201
)
def remove_dislike_from_post(
    post_id: int,
    current_user: Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = utils.remove_dislike(post_id, current_user.user_id, session)
    return post


