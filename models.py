from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Function to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )  # <-- Fix
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )  # <-- Fix


# User Model
class User(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    posts = db.relationship(
        "Post", back_populates="author", cascade="all, delete", lazy="dynamic"
    )
    comments = db.relationship(
        "Comment", back_populates="author", cascade="all, delete", lazy="dynamic"
    )
    likes = db.relationship(
        "Like", back_populates="user", cascade="all, delete", lazy="dynamic"
    )


# Post Model
class Post(BaseModel):
    __tablename__ = "posts"

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author = db.relationship("User", back_populates="posts")
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete", lazy="dynamic"
    )
    likes = db.relationship(
        "Like", back_populates="post", cascade="all, delete", lazy="dynamic"
    )


# Comment Model
class Comment(BaseModel):
    __tablename__ = "comments"

    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(
        db.String(36), db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    author_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id = db.Column(
        db.String(36), db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=["id"]),
        cascade="all, delete",
        lazy="dynamic",
    )


# Like Model
class Like(BaseModel):
    __tablename__ = "likes"

    post_id = db.Column(
        db.String(36), db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    post = db.relationship("Post", back_populates="likes")
    user = db.relationship("User", back_populates="likes")

    __table_args__ = (db.UniqueConstraint("post_id", "user_id", name="unique_like"),)


# Create Tables
with app.app_context():
    db.create_all()

print("Database tables created successfully!")
