from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    data = request.form
    print(data)
    return render_template("login.html", name="login")

@auth.route("/logout")
def logout():
    return "<h1>Logout</h1>"

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
    return render_template("signup.html", name="signup")