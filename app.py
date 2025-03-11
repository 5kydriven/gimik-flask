from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid
from datetime import datetime, timezone

app = Flask(__name__, static_folder="static", template_folder="templates")


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# User Model (No Table Creation)
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now()
    )  # Fixed
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )  # Fixed


# Post Model
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(
        db.String, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship("User", backref=db.backref("posts", cascade="all, delete"))


# Register User
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Validate required fields
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user exists
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({"error": "Username or email already taken"}), 409

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()), username=username, email=email, password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return (
        jsonify({"message": "User registered successfully", "user_id": new_user.id}),
        201,
    )


# Create a New Post
@app.route("/posts", methods=["POST"])
def create_post():
    user_id = request.form.get("user_id")
    title = request.form.get("title")
    content = request.form.get("content")

    if not user_id or not title or not content:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_post = Post(title=title, content=content, author_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return (
        jsonify({"message": "Post created successfully", "post_id": new_post.id}),
        201,
    )


# Get All Posts
@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    post_list = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at.isoformat(),
        }
        for post in posts
    ]
    return jsonify(post_list)


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


# Update a Post
@app.route("/posts/<string:post_id>", methods=["PUT"])
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    data = request.form
    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)

    db.session.commit()
    return jsonify({"message": "Post updated successfully", "post_id": post.id})


# Delete a Post
@app.route("/posts/<string:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"})


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0 ", debug=True)
