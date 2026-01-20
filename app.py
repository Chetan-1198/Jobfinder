from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobfinder.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))

# ================= JOB DATA =================
ALL_JOBS = {
    "Technical Jobs": [
        {"title": "Software Developer / Programmer", "companies": "TCS, Infosys, Wipro, Accenture, Google, Microsoft"},
        {"title": "Web Developer", "companies": "Zoho, Freshworks, Infosys, IBM"},
        {"title": "Mobile App Developer", "companies": "Swiggy, Zomato, Paytm, PhonePe"},
        {"title": "Software Tester (QA)", "companies": "Capgemini, Cognizant, TCS"},
        {"title": "DevOps Engineer", "companies": "Amazon, Microsoft, Accenture"},
    ],
    "Design Jobs": [
        {"title": "UI Designer", "companies": "Zoho, Freshworks"},
        {"title": "UX Designer", "companies": "Google, Amazon"},
        {"title": "Graphic Designer", "companies": "Design Agencies"},
    ],
    "Support & Operations Jobs": [
        {"title": "Technical Support Engineer", "companies": "Wipro, HCL"},
        {"title": "IT Support", "companies": "All IT Companies"},
    ],
    "Management Jobs": [
        {"title": "Project Manager", "companies": "Infosys, TCS"},
        {"title": "Product Manager", "companies": "Google, Amazon"},
    ],
    "Business & Non-Technical Jobs": [
        {"title": "HR Executive", "companies": "Infosys, Wipro"},
        {"title": "Business Analyst", "companies": "Deloitte, EY"},
    ],
    "Entry-Level / Freshers Jobs": [
        {"title": "Intern", "companies": "Startups, IT Companies"},
        {"title": "Graduate Engineer Trainee (GET)", "companies": "TCS, Infosys"},
    ],
}

# ================= ROUTES =================
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Invalid login")
    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        user = User(
            fullname=request.form["fullname"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user, jobs=ALL_JOBS)

# ✅ SAVE JOB
@app.route("/save-job")
def save_job():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.args.get("title")
    company = request.args.get("company")

    saved = SavedJob(user_id=session["user_id"], title=title, company=company)
    db.session.add(saved)
    db.session.commit()

    flash("Job saved successfully ")
    return redirect(url_for("dashboard"))

# ✅ VIEW SAVED JOBS
@app.route("/saved-jobs")
def saved_jobs():
    if "user_id" not in session:
        return redirect(url_for("login"))

    jobs = SavedJob.query.filter_by(user_id=session["user_id"]).all()
    return render_template("jobs.html", jobs=jobs)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)



