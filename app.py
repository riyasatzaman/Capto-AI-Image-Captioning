import logging
import os
import uuid
from io import BytesIO

from flask import (
    Flask,
    abort,
    jsonify,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from captioning import generate_caption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = os.environ.get(
    "UPLOAD_FOLDER", os.path.join(app.root_path, "static", "uploads")
)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _safe_upload_path(filename: str) -> str:
    """Resolve filename inside UPLOAD_FOLDER, rejecting path traversal."""
    folder = os.path.realpath(app.config["UPLOAD_FOLDER"])
    candidate = os.path.realpath(os.path.join(folder, secure_filename(filename)))
    if not candidate.startswith(folder + os.sep):
        abort(400)
    return candidate


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        style = request.form.get("style", "default")
        existing = request.form.get("uploaded_image")

        if existing:
            filepath = _safe_upload_path(existing)
            if not os.path.exists(filepath):
                return render_template(
                    "index.html",
                    uploaded_image=None,
                    caption=None,
                    error="That image is no longer available. Please upload it again.",
                )
            result = generate_caption(filepath, style)
            return render_template(
                "index.html",
                uploaded_image=existing,
                caption=result["caption"],
                source=result["source"],
                style=style,
            )

        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template(
                "index.html", uploaded_image=None, caption=None,
                error="Please choose an image to upload.",
            )
        if not _allowed(file.filename):
            return render_template(
                "index.html", uploaded_image=None, caption=None,
                error="Unsupported file type. Use PNG, JPG, JPEG, WEBP, or GIF.",
            )

        ext = file.filename.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)
        file.save(filepath)

        result = generate_caption(filepath, style)
        return render_template(
            "index.html",
            uploaded_image=stored_name,
            caption=result["caption"],
            source=result["source"],
            style=style,
        )

    return render_template("index.html", uploaded_image=None, caption=None)


@app.route("/api/caption", methods=["POST"])
def api_caption():
    """JSON endpoint used for the regenerate-caption button (no full reload)."""
    style = request.form.get("style", "default")
    existing = request.form.get("uploaded_image", "")
    if not existing:
        return jsonify({"error": "uploaded_image is required"}), 400
    filepath = _safe_upload_path(existing)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image no longer available"}), 404
    result = generate_caption(filepath, style)
    return jsonify(result)


@app.route("/download")
def download_caption():
    text = request.args.get("text", "").strip()
    if not text:
        abort(400)
    buf = BytesIO(text.encode("utf-8"))
    return send_file(
        buf,
        mimetype="text/plain",
        as_attachment=True,
        download_name="capto-caption.txt",
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.errorhandler(413)
def too_large(_e):
    return render_template(
        "index.html", uploaded_image=None, caption=None,
        error=f"File is too large. Max upload size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
    ), 413


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
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
