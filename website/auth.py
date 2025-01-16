from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import yagmail
import uuid

auth = Blueprint("auth", __name__)

admin_email = "interlnkd.info@gmail.com"
app_password = "boya yvsp rvtk ocfj"
email_password = "lnkdadmin123"

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
    
        user = User.query.filter_by(email_address=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Password is incorrect.", category="error")
        else:
            flash("User does not exist.", category="error")
            
    return render_template("login.html", name="Login", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user = User.query.filter_by(email_address=email).first()
        if user:
            flash("User already exists", category="error")  
        elif len(email) < 4:
            flash("Email must be greater than 4 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 2 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password should be at least 7 characters", category="error")
        else:
            new_user = User(email_address=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))
        
            
    return render_template("signup.html", name="Sign up", user=current_user)

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        recipient_email = request.form.get("email")
        user = User.query.filter_by(email_address=recipient_email).first()
        
        flash("Password reset link sent to your email if it is registered with an interLINKED account", category="info")
        
        if user:
            reset_token = uuid.uuid4().hex
            user.reset_token = reset_token
            db.session.commit()
            subject = 'Reset your password for InterLINKED'
            contents = f'<p>Dear {user.first_name},\nA password reset was requested for your interLINKED account.</p><a href="http://localhost:5000/reset_password?reset_token={reset_token}">Reset your password</a>'

            with yagmail.SMTP(admin_email, app_password) as yag:
                yag.send(recipient_email, subject, contents)
                
            
    return render_template("forgot_password.html", name="Forgot Password", user=current_user)
            
@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    reset_token = request.args.get("reset_token")
    user = User.query.filter_by(reset_token=reset_token).first()
    valid_link = True if reset_token and user else False
    
    if valid_link and request.method == "POST":
        new_password = request.form.get("new_password")
        new_password_retype = request.form.get("new_password_retype")
        
        if new_password != new_password_retype:
            flash("Passwords do not match", category="error")
        elif new_password < 7:
            flash("Password is too short", category="error")
        else:
            user.password = generate_password_hash(new_password, method="sha256")
            user.reset_token = ""
            db.session.commit()
            flash("Password reset successful", category="success")
            return redirect(url_for("auth.login"))
            
        
            
    return render_template("reset_password.html", name="Forgot Password", user=current_user, valid_link=valid_link)