from flask import render_template, redirect, session, request, flash
from flask_app import app
from flask_app.models.user import User
from flask_app.models.post import Post
from flask_bcrypt import Bcrypt
bcrypt =Bcrypt(app)

@app.route('/')
def log_and_reg():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template("log_and_reg.html")

@app.route("/users/register", methods=["POST"])
def register():
    if not User.validate_register(request.form):
        # we redirect to the template with the form.
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    # put the pw_hash into the data dictionary
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form['email'],
        "password" : pw_hash
    }
    # Call the save @classmethod on User
    user_id = User.register_user(data)
    # store user id into session
    session['user_id'] = user_id
    return redirect("/dashboard")

@app.route("/users/login", methods=["POST"])
def login():
    print("Start of login function")
    if User.validate_login(request.form):
        data = { "email" : request.form["email"] }
        user_in_db = User.get_user_by_email(data)
        print(user_in_db)
        if not user_in_db:
            print("Did not find the email")
            flash("Email not found", "error")
        else:
            print("We found the email")
            if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
                flash("Invalid Email/Password" , "error")
            else:
                session['user_id'] = user_in_db.id
                return redirect("/dashboard")

    return redirect('/')
    # if not User.validate_login(request.form):
    #     # we redirect to the template with the form.
    #     return redirect('/')

    # # see if the username provided exists in the database
    # data = { "email" : request.form["email"] }
    # user_in_db = User.get_user_by_email(data)
    # if user_in_db is None:
    #     flash("Email not found", "error")
    #     return redirect('/')

    # # user is not registered in the db
    # if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
    #     # if we get False after checking the password
    #     flash("Invalid Email/Password" , "error")
    #     return redirect('/')

    # # if the passwords matched, we set the user_id into session
    # session['user_id'] = user_in_db.id
    # return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    data = {
        "id": session["user_id"]
    }
    user = User.get_user(data)
    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/users/<int:user_id>")
def user(user_id):
    if "user_id" not in session:
        return redirect("/")
    user_data = {
        "id": user_id
    }
    user = User.get_user(user_data)
    data = {
        "user_id": user_id
    }
    user_posts = Post.get_user_posts(data)
    return render_template("user.html", user=user, user_posts=user_posts)
