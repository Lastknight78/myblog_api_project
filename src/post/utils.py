from ..processor_image import delete_image
from ..error import SQLAlchemyDataCreationError
from sqlalchemy.orm import Session
from sqlalchemy import delete
from ..db.models import Comments, Dislikes, Likes, Posts, HashTags, post_hashtag, Users
from . import schemas
from ..error import ItemNotFoundException, OperationNotAllowedException
import re


def return_username_from_user_id(session: Session, user_id):
    user = session.query(Users).filter(Users.user_id == user_id).first()
    return user.username


def post_out_sqlalchemy_to_pydantic(
    session: Session, post: Posts
) -> schemas.PostOutModel:
    hashtags = [hashtag_model.hashtag for hashtag_model in post.hashtags]
    comments = [
        {
            "username": return_username_from_user_id(session, comment.user_id),
            "comment": comment.comment_content,
            "comment_date": comment.commented_at,
        }
        for comment in post.comments
    ]
    liked_by = [
        return_username_from_user_id(session, like.user_id) for like in post.likes
    ]
    disliked_by = [
        return_username_from_user_id(session, dislike.user_id)
        for dislike in post.dislikes
    ]
    post_out = schemas.PostOutModel(
        post_title=post.post_title,
        post_content=post.post_content,
        post_id=post.post_id,
        user_id=post.user_id,
        post_image=post.post_image,
        posted_at=post.posted_at,
        total_likes=len(post.likes),
        total_dislikes=len(post.dislikes),
        total_comments=len(post.comments),
        hashtags=hashtags,
        comments=comments,
        liked_by=liked_by,
        disliked_by=disliked_by,
    )
    return post_out


def get_post_by_id(
    post_id: int, session: Session, return_pydantic=True
) -> Posts | schemas.PostOutModel:
    post = session.query(Posts).filter(Posts.post_id == post_id).first()
    if not post:
        raise ItemNotFoundException(f"Post with id {post_id} not found")
    if return_pydantic:
        post = post_out_sqlalchemy_to_pydantic(session=session, post=post)
    return post


def get_all_posts(session: Session) -> list[schemas.PostOutModel]:
    posts = session.query(Posts).all()
    if posts:
        posts = [
            post_out_sqlalchemy_to_pydantic(session=session, post=post)
            for post in posts
        ]
    return posts


def get_all_user_posts(session: Session, user_id: int) -> list[schemas.PostOutModel]:
    user_posts = session.query(Posts).filter(Posts.user_id == user_id).all()
    if user_posts:
        user_posts = [
            post_out_sqlalchemy_to_pydantic(post=post, session=session)
            for post in user_posts
        ]
    return user_posts


def find_hashtags_in_post(post: Posts) -> list[str]:
    hashtags: list[str] = list(
        set(re.findall(pattern=r"(?<!\S)#\w+", string=post.post_content))
    )
    hashtags = [hashtag.replace("#", "").lower().strip() for hashtag in hashtags]
    return hashtags


def add_new_hashtag(session: Session, hashtag: str, post: Posts) -> None:
    try:
        add_hashtag = HashTags(hashtag=hashtag)
        post.hashtags.append(add_hashtag)
        session.commit()
    except Exception as e:
        raise SQLAlchemyDataCreationError("SQLAlchemy Error(add_hashtags): " + str(e))


def create_new_post(
    post: schemas.PostInModel, session: Session
) -> schemas.PostOutModel:
    try:
        add_post = Posts(**post.model_dump())
        session.add(add_post)
        session.commit()
        session.refresh(add_post)
    except Exception as e:
        raise SQLAlchemyDataCreationError("SQLAlchemy Error(add_post): " + str(e))
    post = get_post_by_id(add_post.post_id, session, return_pydantic=False)
    hashtags = find_hashtags_in_post(post=post)
    if hashtags:
        for hashtag in hashtags:
            add_new_hashtag(session, hashtag, post)
    post = post_out_sqlalchemy_to_pydantic(session=session, post=post)
    return post


def delete_hashtags_from_post(session: Session, hashtag_id: int, post_id: int) -> None:
    assoc = delete(post_hashtag).where(
        post_hashtag.c.post_id == post_id, post_hashtag.c.hashtag_id == hashtag_id
    )
    session.execute(assoc)
    session.commit()


def update_post(
    post_id: int, post_in: schemas.PostUpdateModel, session: Session
) -> schemas.PostOutModel:
    post_query = session.query(Posts).filter(Posts.post_id == post_id)
    post = post_query.first()
    post_in.post_title = post_in.post_title if post_in.post_title else post.post_title
    post_in.post_image = post_in.post_image if post_in.post_image else post.post_image
    post_in.post_content = (
        post_in.post_content if post_in.post_content else post.post_content
    )
    previous_post_hashtags = [hashtag_model.hashtag for hashtag_model in post.hashtags]
    previous_post_hashtags_dict = {
        hashtag_model.hashtag: hashtag_model.hashtag_id
        for hashtag_model in post.hashtags
    }
    try:
        post_query.update(post_in.model_dump())
        session.commit()
    except Exception as e:
        raise SQLAlchemyDataCreationError(str(e))
    new_post_hashtags = find_hashtags_in_post(post=post)
    if previous_post_hashtags:
        if new_post_hashtags:
            for hashtag in previous_post_hashtags:
                if hashtag not in new_post_hashtags:
                    hashtag_id = previous_post_hashtags_dict.get(hashtag)
                    delete_hashtags_from_post(session, hashtag_id, post_id)
            for hashtag in new_post_hashtags:
                if hashtag not in previous_post_hashtags:
                    add_new_hashtag(session, hashtag, post)
        else:
            for hashtag in previous_post_hashtags:
                hashtag_id = previous_post_hashtags_dict.get(hashtag)
                delete_hashtags_from_post(session, hashtag_id, post_id)
    else:
        if new_post_hashtags:
            for hashtag in new_post_hashtags:
                add_new_hashtag(session, hashtag, post)
    post = post_out_sqlalchemy_to_pydantic(session=session, post=post)
    return post


def delete_post(post_id: int, user_id: int, session: Session) -> None:
    post = session.query(Posts).filter(Posts.post_id == post_id).first()
    if not post:
        raise ItemNotFoundException(f"Post with id {post_id} not found")
    if post.user_id != user_id:
        raise OperationNotAllowedException(
            "You are not allowed to make an edit to this post."
        )
    if post.post_image:
        delete_image(post.post_image, session)
    session.delete(post)
    session.commit()


def get_posts_by_hashtags(hashtag: str, session: Session) -> list[schemas.PostOutModel]:
    hashs = session.query(HashTags).filter(HashTags.hashtag == hashtag).all()
    posts = [
        post_out_sqlalchemy_to_pydantic(session=session, post=hash.post)
        for hash in hashs
    ]
    return posts


def add_comment_to_post(
    comment: schemas.CommentInModel, session: Session
) -> schemas.PostOutModel:
    _ = get_post_by_id(comment.post_id, session)
    try:
        add_commnet = Comments(**comment.model_dump())
        session.add(add_commnet)
        session.commit()
        session.refresh(add_commnet)
    except Exception as e:
        raise SQLAlchemyDataCreationError("SQLAlchemy Error(add_post): " + str(e))
    return get_post_by_id(comment.post_id, session)


def delete_comment(comment_id: int, user_id: int, session: Session) -> None:
    comment = session.query(Comments).filter(Comments.comment_id == comment_id).first()
    if not comment:
        raise ItemNotFoundException(f"Comment with id {comment_id} not found")
    if comment.user_id != user_id:
        raise OperationNotAllowedException(
            "You are not allowed to delete to this comment."
        )
    session.delete(comment)
    session.commit()


def edit_comment(
    comment_id: int,
    user_id: int,
    new_comment: schemas.CommentBaseModel,
    session: Session,
) -> Comments:
    comment = session.query(Comments).filter(Comments.comment_id == comment_id).first()
    if not comment:
        raise ItemNotFoundException(f"Comment with id {comment_id} not found")
    if comment.user_id != user_id:
        raise OperationNotAllowedException(
            "You are not allowed to delete to this comment."
        )
    session.query(Comments).filter(Comments.comment_id == comment_id).update(
        new_comment.model_dump()
    )
    session.commit()
    return comment


def remove_like(post_id: int, user_id: int, session: Session):
    like = (
        session.query(Likes)
        .filter((Likes.post_id == post_id) & (Likes.user_id == user_id))
        .first()
    )
    if not like:
        raise ItemNotFoundException("Like id not not found")
    session.delete(like)
    session.commit()
    return get_post_by_id(post_id, session)


def remove_dislike(post_id: int, user_id: int, session: Session):
    dislike = (
        session.query(Dislikes)
        .filter((Dislikes.post_id == post_id) & (Dislikes.user_id == user_id))
        .first()
    )
    if not dislike:
        raise ItemNotFoundException("Disike id not not found")
    session.delete(dislike)
    session.commit()
    return get_post_by_id(post_id, session)


def like_post(post_id: int, user_id: int, session: Session) -> schemas.PostOutModel:
    post = get_post_by_id(post_id=post_id, session=session, return_pydantic=False)
    already_liked = (
        session.query(Likes)
        .filter((Likes.post_id == post_id) & (Likes.user_id == user_id))
        .first()
    )
    if already_liked:
        return post_out_sqlalchemy_to_pydantic(session, post)

    already_disliked = (
        session.query(Dislikes)
        .filter((Dislikes.post_id == post_id) & (Dislikes.user_id == user_id))
        .first()
    )
    if already_disliked:
        remove_dislike(post_id, user_id, session)
    add_like = Likes(user_id=user_id, post_id=post_id)
    session.add(add_like)
    session.commit()
    session.refresh(add_like)
    return post_out_sqlalchemy_to_pydantic(session, post)


def dislike_post(post_id: int, user_id: int, session: Session) -> schemas.PostOutModel:
    post = get_post_by_id(post_id=post_id, session=session, return_pydantic=False)
    already_disliked = (
        session.query(Dislikes)
        .filter((Dislikes.post_id == post_id) & (Dislikes.user_id == user_id))
        .first()
    )
    if already_disliked:
        return post_out_sqlalchemy_to_pydantic(session, post)

    already_liked = (
        session.query(Likes)
        .filter((Likes.post_id == post_id) & (Likes.user_id == user_id))
        .first()
    )
    if already_liked:
        remove_like(post_id, user_id, session)
    add_dislike = Dislikes(user_id=user_id, post_id=post_id)
    session.add(add_dislike)
    session.commit()
    session.refresh(add_dislike)
    return post_out_sqlalchemy_to_pydantic(session, post)
