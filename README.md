# Capto — AI Image Captioning

Capto is a Flask web app that turns any image into a creative caption. Upload a photo, pick a style (default, funny, poetic, witty, formal), and Capto returns a caption you can edit, copy, or download.

It uses the [Salesforce/blip-image-captioning-base](https://huggingface.co/Salesforce/blip-image-captioning-base) model via the Hugging Face Inference API in production, with an optional local-model path for offline development.

- **Live demo:** _Add your Render URL here once deployed_
- **Repo:** https://github.com/riyasatzaman/Capto-AI-Image-Captioning

## Features

- Upload an image and get an AI-generated caption
- Five caption styles: default, funny, poetic, witty, formal
- Inline image preview before upload
- Edit the generated caption right in the page
- Regenerate without re-uploading (AJAX)
- Copy to clipboard, download as `.txt`
- Dark / light mode (persisted in `localStorage`)
- File-type and size validation (max 5 MB; PNG/JPG/JPEG/WEBP/GIF)
- Graceful fallback if the model API is unavailable — the app never crashes

## Stack

- **Backend:** Python 3.11, Flask 3, Gunicorn
- **Model:** BLIP base via Hugging Face Inference API (or local `transformers` for dev)
- **Frontend:** Server-rendered Jinja templates + vanilla JS, Bootstrap 5

## Run locally (HF API mode — recommended)

```bash
git clone https://github.com/riyasatzaman/Capto-AI-Image-Captioning.git
cd Capto-AI-Image-Captioning

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your free HF token from https://huggingface.co/settings/tokens

# Load the env var into your shell (or use any tool that reads .env)
export $(grep -v '^#' .env | xargs)

python app.py
```

Open http://127.0.0.1:5000.

## Run locally (offline / local model)

If you want to run the BLIP model on your machine without an HF token:

```bash
pip install -r requirements-dev.txt
python app.py
```

The first run downloads ~1 GB of model weights into `~/.cache/huggingface/`.

## Deploy to Render (free tier)

1. Push this repo to GitHub.
2. Sign in at https://render.com and click **New → Web Service**.
3. Connect your GitHub account and pick the `Capto-AI-Image-Captioning` repo.
4. Render auto-detects `render.yaml`. Confirm:
   - **Environment:** Python
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 60 --workers 2`
   - **Plan:** Free
5. Under **Environment**, add:
   - `HF_API_TOKEN` = your token from https://huggingface.co/settings/tokens
6. Click **Create Web Service**. First deploy takes ~3 minutes.

Your app is live at `https://<service-name>.onrender.com`.

> Free Render services sleep after 15 minutes of inactivity. The first request after a sleep takes ~30 seconds — this is expected.

## Project layout

```
.
├── app.py                  # Flask routes, file validation, error handling
├── captioning.py           # HF API → local model → fallback chain
├── requirements.txt        # Production deps (lightweight)
├── requirements-dev.txt    # Adds torch + transformers for offline dev
├── runtime.txt             # Python version for Render
├── render.yaml             # One-click Render config
├── Procfile                # Gunicorn entrypoint
├── .env.example            # HF_API_TOKEN placeholder
├── static/uploads/         # Ephemeral upload dir (gitignored)
└── templates/
    ├── index.html          # Captioner UI
    ├── home.html           # Marketing landing (/home)
    ├── about.html
    ├── updates.html
    └── contact.html
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `HF_API_TOKEN` | Yes (prod) | Hugging Face token for the Inference API |
| `HF_MODEL` | No | Override model id (default `Salesforce/blip-image-captioning-base`) |
| `HF_TIMEOUT` | No | API timeout in seconds (default `30`) |
| `PORT` | No | Set automatically by Render |
| `FLASK_DEBUG` | No | Set to `1` for debug mode locally |

## How it falls back

`captioning.py` tries each backend in order; if all fail the app still returns a friendly placeholder caption instead of erroring out:

1. HF Inference API (if `HF_API_TOKEN` is set)
2. Local BLIP via `transformers` (if installed)
3. Stubbed caption — keeps the demo usable even when offline

## License

MIT — see `LICENSE`.

## Contact

- Email: riyasatzaman@gmail.com
- GitHub: [@riyasatzaman](https://github.com/riyasatzaman)
