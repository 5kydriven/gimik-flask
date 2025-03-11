from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Function to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())


# User Model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    posts = db.relationship("Post", back_populates="author", cascade="all, delete")
    comments = db.relationship(
        "Comment", back_populates="author", cascade="all, delete"
    )
    likes = db.relationship("Like", back_populates="user", cascade="all, delete")


# Post Model
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    author = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post", cascade="all, delete")
    likes = db.relationship("Like", back_populates="post", cascade="all, delete")


# Comment Model
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(
        db.String, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    author_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id = db.Column(
        db.String, db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    replies = db.relationship(
        "Comment", backref=db.backref("parent", remote_side=[id]), cascade="all, delete"
    )


# Like Model
class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    post_id = db.Column(
        db.String, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    post = db.relationship("Post", back_populates="likes")
    user = db.relationship("User", back_populates="likes")

    __table_args__ = (db.UniqueConstraint("post_id", "user_id", name="unique_like"),)


# Create Tables
with app.app_context():
    db.create_all()

print("Database tables created successfully!")
