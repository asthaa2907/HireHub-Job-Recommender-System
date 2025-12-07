# ---------------------------------------------------------
#  HireHub — Final Corrected app.py (Option C: Save resume path in DB)
# ---------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from recommender import Recommender
from resume_parser import extract_text_from_file
from skill_extractor import extract_skills
import os

# Authentication imports
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
#  Flask App Initialization
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hirehub_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hirehub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------
#  User Model
# ---------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    resume_path = db.Column(db.String(500))  # Store resume file location

# ---------------------------------------------------------
#  Login Manager
# ---------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------------------------------------
#  File Upload Settings
# ---------------------------------------------------------
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------------------------------------
#  Load Recommender (unchanged)
# ---------------------------------------------------------
rec = Recommender(data_path="data/combined_jobs_enriched.csv")


# ---------------------------------------------------------
#  HOME PAGE
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", results=None, title="HireHub")


# ---------------------------------------------------------
#  SEARCH RECOMMENDER
# ---------------------------------------------------------
@app.route("/recommend")
def recommend():
    q = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    experience = request.args.get("experience", "").strip()

    if not q:
        return render_template("index.html", results=None, title="HireHub")

    results = rec.recommend_text(q, top_n=10, location=location, experience=experience)
    return render_template("index.html", results=results, title="Results")


# ---------------------------------------------------------
#  SIGNUP PAGE
# ---------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already exists")

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------------------------------------------------
#  LOGIN PAGE
# ---------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template("login.html", error="Email not found")

        if not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect password")

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")


# ---------------------------------------------------------
#  LOGOUT
# ---------------------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ---------------------------------------------------------
#  PROFILE PAGE (simple version)
# ---------------------------------------------------------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


# ---------------------------------------------------------
#  UPLOAD RESUME + RECOMMENDATIONS
# ---------------------------------------------------------
@app.route("/upload_resume", methods=["GET", "POST"])
@login_required
def upload_resume():

    if request.method == "GET":
        return render_template(
            "upload.html",
            results=None,
            skills=None,
            uploaded_filename=None,
            file_url=None,
            title="Upload Resume"
        )

    file = request.files.get("resume")
    if not file:
        return render_template("upload.html", error="No file uploaded.")

    filename = file.filename.replace("\\", "/").split("/")[-1]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    # Save resume path to logged-in user's profile
    if current_user.is_authenticated:
        current_user.resume_path = filename  # you can choose filename OR filepath
        db.session.commit()

    # Extract text SAFELY
    text = extract_text_from_file(filepath)

    skills = extract_skills(text)
    query_text = " ".join(skills) if skills else text

    results = rec.recommend_text(query_text, top_n=10)
    file_url = f"/uploads/{filename}"

    return render_template(
        "upload.html",
        results=results,
        skills=skills,
        uploaded_filename=filename,
        file_url=file_url,
        title="Resume Recommendations"
    )


# ---------------------------------------------------------
#  Serve Uploaded Files
# ---------------------------------------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------------------------------------------------
#  CHATBOT
# ---------------------------------------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip().lower()

    if not user_input:
        return jsonify({"reply": "Please type a message I can respond to."})

    if any(w in user_input for w in ["hello", "hi", "hey"]):
        reply = "Hello 👋! How can I help you today?"
    elif "upload" in user_input or "resume" in user_input:
        reply = "Click ‘Upload Resume’ to get job recommendations based on your skills."
    elif "help" in user_input:
        reply = "Try searching jobs or upload your resume for personalized results!"
    else:
        reply = "I'm still learning! Ask me about job search or resume upload."

    return jsonify({"reply": reply})


# ---------------------------------------------------------
#  RUN APP
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
