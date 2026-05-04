# Capto — AI Image Captioning

Capto is a Flask web app that turns any image into a social-media-ready caption. Upload a photo, pick a tone (default · funny · poetic · witty · formal), and Capto returns a caption you can edit, copy, or download.

It's built around a **vision-language model** (Qwen3-VL by default) served via Hugging Face's Inference Providers router, with a local BLIP fallback for offline development and a friendly stub fallback so the app never crashes.

- **Live demo:** [capto.onrender.com](https://your-service-name.onrender.com)
- **Repo:** https://github.com/riyasatzaman/Capto-AI-Image-Captioning

## Features

- Upload an image, get an AI-generated caption that reflects what's actually in the frame
- Five caption styles: default, funny, poetic, witty, formal
- Inline preview before upload, drag-and-drop dropzone
- Edit the generated caption inline; auto-fitting textarea (no internal scrollbars)
- Regenerate without re-uploading (AJAX)
- Copy to clipboard, download as `.txt`
- Persistent dark / light mode
- File-type and size validation (max 5 MB; PNG/JPG/JPEG/WEBP/GIF)
- Path-traversal-safe upload handling, UUID-renamed files
- Three-tier graceful fallback — if every backend fails, the app still loads

## Stack

- **Backend:** Python 3.11, Flask 3, Gunicorn
- **Model:** Qwen3-VL via Hugging Face Inference Providers (OpenAI-compatible chat endpoint), with `requirements-dev.txt` adding local BLIP via `transformers` for offline development
- **Frontend:** Server-rendered Jinja templates, vanilla JS, Anton + Inter via Google Fonts — no framework, no build step

## Run locally

```bash
git clone https://github.com/riyasatzaman/Capto-AI-Image-Captioning.git
cd Capto-AI-Image-Captioning

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and paste your free HF token from https://huggingface.co/settings/tokens
export $(grep -v '^#' .env | xargs)

python app.py
```

Open http://127.0.0.1:5000.

### Optional: run the model locally (offline)

If you want the BLIP fallback to run on your machine without an HF token:

```bash
pip install -r requirements-dev.txt
python app.py
```

The first run downloads ~1 GB of weights into `~/.cache/huggingface/`. Heavy and slow — only useful for fully offline development.

## Deploy to Render (free tier)

1. Push this repo to GitHub.
2. Sign in at https://render.com and click **New → Web Service**.
3. Connect your GitHub account and pick the `Capto-AI-Image-Captioning` repo.
4. Render auto-detects [`render.yaml`](render.yaml). Confirm:
   - **Environment:** Python
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --threads 4`
   - **Plan:** Free
5. Under **Environment**, add `HF_API_TOKEN` with your token from https://huggingface.co/settings/tokens.
6. Click **Create Web Service**. First deploy takes ~3 minutes.

Live at `https://<service-name>.onrender.com`.

> Free Render services sleep after 15 minutes of inactivity. The first request after a sleep takes ~30 seconds to wake the dyno — this is expected, not a bug.

## Project layout

```
.
├── app.py                  # Flask routes, file validation, error handling
├── captioning.py           # VLM (HF) → local BLIP → fallback chain
├── requirements.txt        # Production deps (lightweight)
├── requirements-dev.txt    # Adds torch + transformers for offline dev
├── runtime.txt             # Python version for Render
├── render.yaml             # One-click Render config
├── Procfile                # Gunicorn entrypoint
├── .env.example            # HF_API_TOKEN placeholder
├── static/uploads/         # Ephemeral upload dir (gitignored)
└── templates/
    ├── index.html          # Captioner — upload, generate, edit, regenerate
    ├── about.html
    ├── updates.html
    └── contact.html
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `HF_API_TOKEN` | Yes (prod) | Hugging Face token for the Inference Providers router |
| `HF_VLM_MODELS` | No | Comma-separated list of VLMs to try in order. Default: `Qwen/Qwen3-VL-8B-Instruct,Qwen/Qwen3-VL-30B-A3B-Instruct,Qwen/Qwen2.5-VL-72B-Instruct` |
| `HF_TIMEOUT` | No | Per-request timeout in seconds (default `60`) |
| `LOCAL_BLIP_MODEL` | No | Override the local BLIP fallback model id (default `Salesforce/blip-image-captioning-base`) |
| `PORT` | No | Set automatically by Render |
| `FLASK_DEBUG` | No | Set to `1` for debug mode locally |

## How it falls back

`captioning.py` tries each backend in order and returns at the first one that succeeds:

1. **VLM via HF Inference Providers** — primary path, single call, image-aware (requires `HF_API_TOKEN`)
2. **Local BLIP via `transformers`** — only if `requirements-dev.txt` is installed; wraps the BLIP description in a style-specific template
3. **Stubbed caption** — final fallback so the demo stays usable even when everything else is offline

## License

MIT — see `LICENSE`.

## Contact

- Email: riyasatzaman@gmail.com
- GitHub: [@riyasatzaman](https://github.com/riyasatzaman)
