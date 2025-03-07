import random
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_path, style="default", retry=False):
    """Generates a caption for an image with a specified style, adding randomness."""
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        caption_ids = model.generate(**inputs, max_length=30, do_sample=True, top_k=50, top_p=0.95)
    
    base_caption = processor.decode(caption_ids[0], skip_special_tokens=True)

    # Style variations
    styles = {
        "funny": [
            f"{base_caption} 😂",
            f"Looks like {base_caption}... but funnier!",
            f"Is this {base_caption} or am I dreaming? 😆",
            f"{base_caption}... but with a twist! 🤣"
        ],
        "poetic": [
            f"A moment captured where {base_caption.lower()} dances in light...",
            f"As the world spins, {base_caption.lower()} remains timeless...",
            f"The beauty of {base_caption.lower()} speaks to the soul...",
            f"In this scene, {base_caption.lower()} tells a silent tale..."
        ],
        "witty": [
            f"{base_caption}... or is it? 🤔",
            f"If {base_caption} had a mind, what would it say? 🤯",
            f"Okay, this is definitely {base_caption}. Or is AI fooling us? 🤨",
            f"{base_caption}? AI is trying its best, okay! 😆"
        ],
        "formal": [
            f"According to AI analysis, this is an image of {base_caption}.",
            f"An objective description: {base_caption}.",
            f"This appears to be a representation of {base_caption}.",
            f"In professional terms, we identify this as {base_caption}."
        ],
        "default": [
            f"{base_caption}",
            f"A scene featuring {base_caption}.",
            f"This image contains {base_caption}.",
            f"One way to describe this: {base_caption}."
        ]
    }

    # Return a random variation
    return random.choice(styles.get(style, [base_caption]))