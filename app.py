from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
from captioning import generate_caption  # Import AI logic

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        file = request.files.get("file")
        style = request.form.get("style", "default")  # Default style for first caption
        retry = request.form.get("retry")  # Detect Retry button click

        if retry:  # If retry is clicked, regenerate caption with selected theme
            filename = request.form.get("uploaded_image")  # Get existing image filename
            if filename:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                caption = generate_caption(filepath, style)  # Generate caption with new theme
                return render_template("index.html", uploaded_image=filename, caption=caption)

        if file:  # New image upload (generate default caption)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Generate caption in "Default" theme
            caption = generate_caption(filepath, "default")
            return render_template("index.html", uploaded_image=filename, caption=caption)

    return render_template("index.html", uploaded_image=None, caption=None)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/updates")
def updates():
    return render_template("updates.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)