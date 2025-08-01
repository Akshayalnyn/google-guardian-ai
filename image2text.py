# image2text.py

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import os

# --------------------------------------
# Local Model Path (no internet, no Hugging Face hub)
# --------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_blip_local():
    try:
        processor = BlipProcessor.from_pretrained(
            MODEL_DIR, local_files_only=True, use_fast=False
        )
        model = BlipForConditionalGeneration.from_pretrained(
            MODEL_DIR, local_files_only=True
        ).to(device)
        return processor, model
    except Exception as e:
        print(f"❌ Failed to load BLIP from {MODEL_DIR}: {e}")
        exit(1)


processor, model = load_blip_local()


# --------------------------------------
# Describe Image (Security-Contextual Captioning)
# --------------------------------------
def describe_image(image_path, security_mode=True):
    """
    Returns a structured, context-aware caption from a local image.
    """
    if not os.path.exists(image_path):
        return "[Error] Image file not found."

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)

        output = model.generate(**inputs, max_length=50)
        raw_caption = processor.decode(output[0], skip_special_tokens=True).strip()

        if security_mode:
            return f"Scene description: {raw_caption}. "
        else:
            return raw_caption

    except Exception as e:
        return f"[Error] Image processing failed: {e}"


# --------------------------------------
# CLI Debug/Test Mode
# --------------------------------------
if __name__ == "__main__":
    print("📸 Guardian AI — Local Image-to-Text (BLIP)")
    image_path = input("Enter path to image: ").strip()
    result = describe_image(image_path)
    print("\n📝 Image Description:\n", result)
