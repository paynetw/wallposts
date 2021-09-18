from flask import render_template, redirect, session, request, flash
from flask_app import app
from flask_app.models.post import Post
from flask_app.models.user import User

@app.route('/wall')
def the_wall():
    data = {
        "id": session["user_id"]
    }
    user = User.get_user(data)
    posts = Post.get_all_posts()
    posts_user_liked = Post.get_all_user_liked_posts(data)
    return render_template("wall.html", user=user, posts=posts, posts_user_liked=posts_user_liked)

@app.route('/posts/<int:post_id>/like')
def like(post_id):
    data = {
        "post_id": post_id,
        "user_id": session['user_id']
    }
    Post.like_post(data)

    return redirect("/wall")

@app.route('/posts/<int:post_id>/dislike')
def dislike(post_id):
    data = {
        "post_id": post_id,
        "user_id": session['user_id']
    }
    Post.dislike_post(data)

    return redirect("/wall")


@app.route('/users/<int:user_id>/post', methods=["POST"])
def post_on_wall(user_id):
    
    if not Post.validate_post(request.form):
        return redirect("/wall")
    data = {
        "content": request.form["content"],
        "user_id": user_id
    }
    Post.add_post(data)
    return redirect("/wall")

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    data = {
        "id": post_id
    }
    post = Post.get_post(data)

    return render_template("edit_post.html", post=post)

@app.route('/posts/<int:post_id>/update', methods=["POST"])
def update_post(post_id):
    data = {
        "id": post_id,
        "content": request.form["content"]
    }
    Post.update(data)
    return redirect(f"/posts/{post_id}/edit")

@app.route('/posts/<int:post_id>/delete')
def delete(post_id):
    data = {
        "id": post_id
    }
    Post.delete(data)
    return redirect("/wall")