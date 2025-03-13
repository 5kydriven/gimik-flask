from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_session import Session
import uuid
from datetime import datetime, timezone

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key_here"  # Required for session security
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)  # Initialize session


# User Model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    author = db.relationship("User", backref=db.backref("posts", cascade="all, delete"))
    likes = db.relationship(
        "Like", back_populates="post", cascade="all, delete", lazy="dynamic"
    )

    @property
    def likes_count(self):
        return self.likes.count()


# Like Model
class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(
        db.String, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    post = db.relationship("Post", back_populates="likes")
    user = db.relationship("User", backref="likes")

    __table_args__ = (db.UniqueConstraint("post_id", "user_id", name="unique_like"),)


# Register User
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({"error": "Username or email already taken"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(
        id=str(uuid.uuid4()), username=username, email=email, password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return (
        jsonify({"message": "User registered successfully", "user_id": new_user.id}),
        201,
    )


# Login User
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user.id  # Store user ID in session
    session["username"] = user.username

    return jsonify(
        {"message": "Login successful", "user_id": user.id, "username": user.username}
    )


# Logout User
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear all session data
    return jsonify({"message": "Logged out successfully"})


@app.route("/posts", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    content = request.form.get("content")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    new_post = Post(content=content, author_id=session["user_id"])
    db.session.add(new_post)
    db.session.commit()

    return (
        jsonify({"message": "Post created successfully", "post_id": new_post.id}),
        201,
    )


# Function to Convert UTC to Local Time (e.g., Asia/Manila)
import pytz


def convert_to_localtime(utc_dt, timezone_str="Asia/Manila"):
    if utc_dt is None:
        return None
    local_tz = pytz.timezone(timezone_str)
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)


# Get a Specific Post
@app.route("/posts/<string:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    return jsonify(
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at.isoformat(),
        }
    )


@app.route("/like/<string:post_id>", methods=["POST"])
def like_post(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return (
            jsonify({"message": "Like removed", "likes_count": post.likes_count}),
            200,
        )

    new_like = Like(post_id=post_id, user_id=user_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "Post liked", "likes_count": post.likes_count}), 201


# Get Likes Count for a Post
@app.route("/post/<string:post_id>/likes", methods=["GET"])
def get_post_likes(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({"post_id": post.id, "likes_count": post.likes_count}), 200


# Check If User Liked a Post
@app.route("/post/<string:post_id>/is_liked", methods=["GET"])
def is_post_liked(post_id):
    if "user_id" not in session:
        return jsonify({"is_liked": False})

    user_id = session["user_id"]
    is_liked = (
        Like.query.filter_by(post_id=post_id, user_id=user_id).first() is not None
    )

    return jsonify({"post_id": post_id, "user_id": user_id, "is_liked": is_liked})


@app.route("/", methods=["GET"])
def home():
    if "user_id" in session:
        user = {"id": session["user_id"], "username": session["username"]}
    else:
        user = None

    posts = Post.query.order_by(Post.created_at.desc()).all()

    post_list = [
        {
            "id": post.id,
            "content": post.content,
            "author_id": post.author_id,
            "author_name": post.author.username,
            "created_at": convert_to_localtime(post.created_at).isoformat(),
            "likes_count": post.likes.count(),  # ✅ FIXED
            "liked_by_user": bool(
                Like.query.filter_by(
                    post_id=post.id, user_id=session.get("user_id")
                ).first()
            ),
        }
        for post in posts
    ]
    return render_template("index.html", posts=post_list, user=user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
