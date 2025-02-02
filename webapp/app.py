from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from config import web_config
from globals import proxy_stats, host_stats, brute_stats, active_tasks

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{web_config['db_user']}:{web_config['db_pass']}@{web_config['db_host']}/{web_config['db_name']}"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_login = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.first_login:
                return redirect(url_for("change_password"))
            return redirect(url_for("dashboard"))

        flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_password = request.form["password"]
        current_user.password_hash = generate_password_hash(new_password)
        current_user.first_login = False
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("change_password.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", proxy_stats=proxy_stats, host_stats=host_stats, brute_stats=brute_stats, active_tasks=active_tasks)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(host=web_config["host"], port=web_config["port"], debug=web_config["debug"])
