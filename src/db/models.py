from sqlalchemy import Column, Integer, Table, Text, ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, Relationship
from datetime import datetime, timezone, date
from .database import Base
from ..settings.config import config
import uuid

date_now = datetime.now(timezone.utc)


class ImageMapper(Base):
    __tablename__ = "image_mapper"

    image_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    image_name = Column(String, nullable=False)
    image_url = Column(String, nullable=False)


class EmailToken(Base):
    __tablename__ = "email_token"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    old_email: Mapped[str] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)


class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    firstname: Mapped[str] = mapped_column(nullable=False)
    lastname: Mapped[str] = mapped_column(nullable=False)
    dob: Mapped[date] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    acct_deactivated: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: date_now)
    image_url: Mapped[str] = mapped_column(default=config.DEFAULT_PROFILE_IMAGE)
    posts = Relationship(
        "Posts", back_populates="user", uselist=True, cascade="all, delete"
    )


post_hashtag = Table(
    "post_hashtag",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.post_id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.hashtag_id"), primary_key=True),
)


class Posts(Base):
    __tablename__ = "posts"
    post_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    post_title: Mapped[str] = mapped_column(nullable=False)
    post_content: Mapped[str] = mapped_column(Text, nullable=False)
    post_image: Mapped[str] = mapped_column(nullable=True)
    posted_at: Mapped[datetime] = mapped_column(default=lambda: date_now)
    user = Relationship("Users", back_populates="posts", uselist=False)
    comments = Relationship(
        "Comments", back_populates="post", uselist=True, cascade="all, delete"
    )
    likes = Relationship(
        "Likes", back_populates="post", uselist=True, cascade="all, delete"
    )
    dislikes = Relationship(
        "Dislikes", back_populates="post", uselist=True, cascade="all, delete"
    )
    hashtags = Relationship(
        "HashTags",
        secondary=post_hashtag,
        back_populates="post",
        cascade="all, delete",
    )


class Comments(Base):
    __tablename__ = "comments"
    comment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"))
    comment_content: Mapped[str] = mapped_column(Text, nullable=False)
    commented_at: Mapped[datetime] = mapped_column(default=lambda: date_now)
    post = Relationship("Posts", back_populates="comments", uselist=False)


class Likes(Base):
    __tablename__ = "likes"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"), primary_key=True)
    post = Relationship("Posts", back_populates="likes", uselist=False)


class Dislikes(Base):
    __tablename__ = "dislikes"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"), primary_key=True)
    post = Relationship("Posts", back_populates="dislikes", uselist=False)


class HashTags(Base):
    __tablename__ = "hashtags"
    hashtag_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hashtag: Mapped[str] = mapped_column(nullable=False)
    post = Relationship(
        "Posts", secondary=post_hashtag, uselist=False, back_populates="hashtags"
    )
