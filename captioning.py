"""Image captioning via a vision-language model.

Primary path: Hugging Face Inference Providers (OpenAI-compatible chat
endpoint) with a small VLM that takes the image and a style prompt and
returns a finished caption in one call.

Fallback path 1: a local BLIP model (only loads if `transformers` is
installed; install requirements-dev.txt to enable).

Fallback path 2: a friendly stub caption wrapped by a style template.
The app never raises on failure - if every backend is down, the demo
still loads.
"""

from __future__ import annotations

import base64
import json
import logging
import mimetypes
import os
import random
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "").strip()
HF_TIMEOUT = int(os.environ.get("HF_TIMEOUT", "60"))

# OpenAI-compatible chat completions on the HF router. Vision-language
# models accept images via data URLs in the message content.
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
VLM_MODELS = [
    m.strip()
    for m in os.environ.get(
        "HF_VLM_MODELS",
        "Qwen/Qwen3-VL-8B-Instruct,Qwen/Qwen3-VL-30B-A3B-Instruct,Qwen/Qwen2.5-VL-72B-Instruct",
    ).split(",")
    if m.strip()
]

LOCAL_BLIP_MODEL = os.environ.get("LOCAL_BLIP_MODEL", "Salesforce/blip-image-captioning-base")

_local_pipeline = None


STYLE_PROMPTS = {
    "default": (
        "Write one short, natural caption for this image, suitable for a "
        "social media post. Keep it accurate, vivid, and concise (one "
        "sentence, under 20 words). Output only the caption."
    ),
    "funny": (
        "Write one short, witty, funny social-media caption for this image. "
        "Light humor, a relatable joke or observation. One sentence, under "
        "20 words. Up to two emojis allowed. Output only the caption."
    ),
    "poetic": (
        "Write one short, poetic, evocative caption for this image. "
        "Lyrical language, sensory imagery. No emojis. One sentence, "
        "under 20 words. Output only the caption."
    ),
    "witty": (
        "Write one short, clever, witty caption for this image with a smart "
        "turn of phrase. Subtle humor. No emojis. One sentence, under 20 "
        "words. Output only the caption."
    ),
    "formal": (
        "Write one short, formal, descriptive caption for this image. "
        "Clear, professional, no slang, no emojis. One sentence, under 20 "
        "words. Output only the caption."
    ),
}

STYLE_TEMPLATES = {
    "default": ["{c}", "A scene featuring {c}.", "This image shows {c}.", "One way to describe this: {c}."],
    "funny": [
        "{c} \U0001F602",
        "Looks like {c}... but funnier!",
        "{c}... but with a twist! \U0001F923",
    ],
    "poetic": [
        "A moment captured where {cl} dances in the light...",
        "As the world turns, {cl} remains timeless.",
        "The beauty of {cl} speaks softly to the soul.",
    ],
    "witty": [
        "{c}... or is it?",
        "If {cl} could talk, what stories it would tell.",
        "Definitely {cl}. Probably. Maybe.",
    ],
    "formal": [
        "An objective description: {c}.",
        "This appears to be a representation of {cl}.",
        "The image depicts {cl}.",
    ],
}


def _strip_quotes(s: str) -> str:
    s = s.strip()
    while s and s[0] in ("“", "”", '"', "'"):
        s = s[1:]
    while s and s[-1] in ("“", "”", '"', "'"):
        s = s[:-1]
    return s.strip()


def _data_url_for(image_path: str) -> str:
    mime, _ = mimetypes.guess_type(image_path)
    if not mime:
        mime = "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _caption_via_vlm(image_path: str, style: str) -> Optional[str]:
    """Single-call VLM captioning. Returns the caption or None on failure."""
    if not HF_API_TOKEN:
        return None
    prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["default"])
    data_url = _data_url_for(image_path)
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    for model in VLM_MODELS:
        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": 80,
            "temperature": 0.8,
        }
        try:
            r = requests.post(HF_CHAT_URL, headers=headers, json=body, timeout=HF_TIMEOUT)
        except requests.RequestException as exc:
            logger.warning("VLM request failed (%s): %s", model, exc)
            continue
        if r.status_code == 503:
            time.sleep(2)
            try:
                r = requests.post(HF_CHAT_URL, headers=headers, json=body, timeout=HF_TIMEOUT)
            except requests.RequestException:
                continue
        if r.status_code != 200:
            logger.warning("VLM %s -> %s: %s", model, r.status_code, r.text[:200])
            continue
        try:
            payload = r.json()
            text = payload["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError):
            logger.warning("Unexpected VLM payload from %s", model)
            continue
        text = _strip_quotes(text)
        first_line = next((ln for ln in (l.strip() for l in text.splitlines()) if ln), text)
        cleaned = _strip_quotes(first_line)
        if cleaned:
            return cleaned
    return None


def _try_load_local_blip():
    global _local_pipeline
    if _local_pipeline is not None:
        return _local_pipeline
    try:
        from PIL import Image  # noqa: F401
        from transformers import BlipForConditionalGeneration, BlipProcessor
        import torch

        processor = BlipProcessor.from_pretrained(LOCAL_BLIP_MODEL)
        model = BlipForConditionalGeneration.from_pretrained(LOCAL_BLIP_MODEL)
        _local_pipeline = ("blip", processor, model, torch)
        logger.info("Loaded local BLIP model %s", LOCAL_BLIP_MODEL)
        return _local_pipeline
    except Exception as exc:  # noqa: BLE001
        logger.info("Local BLIP unavailable (%s); will use VLM API or fallback.", exc)
        _local_pipeline = ("unavailable",)
        return _local_pipeline


def _caption_via_local_blip(image_path: str) -> Optional[str]:
    pipe = _try_load_local_blip()
    if not pipe or pipe[0] != "blip":
        return None
    _, processor, model, torch = pipe
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        ids = model.generate(**inputs, max_length=40, do_sample=True, top_k=50, top_p=0.95)
    return processor.decode(ids[0], skip_special_tokens=True).strip()


def _template_wrap(description: str, style: str) -> str:
    templates = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["default"])
    return random.choice(templates).format(c=description, cl=description.lower())


def generate_caption(image_path: str, style: str = "default") -> dict:
    """Return {"caption": str, "source": str, "error": str|None}."""
    try:
        # Primary path: VLM via HF Inference Providers (one call, image-aware).
        cap = _caption_via_vlm(image_path, style)
        if cap:
            return {"caption": cap, "source": "vlm", "error": None}

        # Dev fallback: local BLIP + style template.
        local = _caption_via_local_blip(image_path)
        if local:
            return {
                "caption": _template_wrap(local, style),
                "source": "local",
                "error": None,
            }

        # Last resort.
        return {
            "caption": _template_wrap("an interesting image", style),
            "source": "fallback",
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Caption generation failed")
        return {
            "caption": "Could not generate a caption for this image.",
            "source": "error",
            "error": str(exc),
        }
