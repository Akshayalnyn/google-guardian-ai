# image2text.py

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import os
import zipfile
import requests
from io import BytesIO

# --------------------------------------
# Model Setup from GitHub Release
# --------------------------------------
MODEL_URL = "https://github.com/Akshayalnyn/google-guardian-ai/releases/download/v1.0.0/model.zip"
MODEL_ZIP_PATH = "model.zip"
MODEL_DIR = "downloaded_models"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def download_model_zip():
    """Downloads the model zip file from GitHub Releases if not present."""
    if os.path.exists(MODEL_ZIP_PATH):
        print("📦 Model zip already exists.")
        return True

    print(f"⬇️ Downloading model from GitHub Releases...\n{MODEL_URL}")
    try:
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        with open(MODEL_ZIP_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Model zip downloaded successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False


def extract_model_zip():
    """Extracts the model zip file to the target directory."""
    if os.path.exists(MODEL_DIR) and os.path.exists(
        os.path.join(MODEL_DIR, "config.json")
    ):
        print("✅ Image model already extracted.")
        return True

    if not os.path.exists(MODEL_ZIP_PATH):
        print(f"❌ Model zip file not found at {MODEL_ZIP_PATH}")
        return False

    try:
        print("📦 Extracting image model zip...")
        with zipfile.ZipFile(MODEL_ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        print("✅ Extraction successful.")
        return True
    except Exception as e:
        print(f"❌ Failed to extract model zip: {e}")
        return False


# Download and extract model
if not (download_model_zip() and extract_model_zip()):
    raise RuntimeError("❌ Model setup failed.")


def load_blip_local():
    try:
        processor = BlipProcessor.from_pretrained(MODEL_DIR, local_files_only=True)
        model = BlipForConditionalGeneration.from_pretrained(
            MODEL_DIR, local_files_only=True
        ).to(device)
        return processor, model
    except Exception as e:
        print(f"❌ Failed to load BLIP from {MODEL_DIR}: {e}")
        exit(1)


processor, model = load_blip_local()


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
    image_path = input("Enter path to image: ").strip()
    result = describe_image(image_path)
    print("\n📝 Image Description:\n", result)
