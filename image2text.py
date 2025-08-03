# image2text.py

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import os

# --------------------------------------
# Model Configuration
# --------------------------------------
# Use Hugging Face model directly instead of Google Drive
MODEL_NAME = (
    "Salesforce/blip-image-captioning-base"  # Official BLIP model from Hugging Face
)
MODEL_DIR = "downloaded_models"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_blip_model():
    """Load the BLIP model from cache or download if needed."""
    try:
        print("🔄 Loading BLIP model...")

        # Create cache directory if it doesn't exist
        os.makedirs(MODEL_DIR, exist_ok=True)

        # Load from Hugging Face (will download if not cached, load from cache if available)
        print(f"📦 Loading {MODEL_NAME}...")
        processor = BlipProcessor.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)
        model = BlipForConditionalGeneration.from_pretrained(
            MODEL_NAME, cache_dir=MODEL_DIR
        ).to(device)

        print("✅ Model loaded successfully!")
        return processor, model

    except Exception as e:
        print(f"❌ Failed to load BLIP model: {e}")
        print("💡 Make sure you have internet connection for first-time download")
        exit(1)


processor, model = load_blip_model()


def describe_image(image_path, security_mode=True):
    """Generates a contextual image description."""
    if not os.path.exists(image_path):
        return "[Error] Image file not found."

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        output = model.generate(**inputs, max_length=50)
        raw_caption = processor.decode(output[0], skip_special_tokens=True).strip()
        return f"Scene description: {raw_caption}." if security_mode else raw_caption
    except Exception as e:
        return f"[Error] Image processing failed: {e}"


# --------------------------------------
# CLI Debug/Test Mode
# --------------------------------------
if __name__ == "__main__":
    print("📸 Guardian AI — Local Image-to-Text (BLIP)")
    image_path = "C:/Users/aksha/Downloads/download.jpg"
    result = describe_image(image_path)
    print("\n📝 Image Description:\n", result)
