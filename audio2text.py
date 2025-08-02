import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import os
import zipfile
import requests
from model_cache_manager import cache_manager

# GitHub release URL for the Whisper model zip
MODEL_URL = "https://github.com/Akshayalnyn/google-guardian-ai/releases/download/v1.0.0/audio_model.zip"
MODEL_ZIP_PATH = "audio_model.zip"
LOCAL_MODEL_DIR = cache_manager.get_model_path("audio")


def download_and_extract_model():
    """Download and extract Whisper model zip from GitHub Releases."""
    # Skip if already extracted and valid
    if cache_manager.is_cache_valid("audio", LOCAL_MODEL_DIR):
        print("✅ Using cached audio models")
        cache_manager.mark_accessed("audio")
        return True

    try:
        print(f"⬇️ Downloading audio model from:\n{MODEL_URL}")
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()

        with open(MODEL_ZIP_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Model zip downloaded.")

        print("📦 Extracting audio model...")
        with zipfile.ZipFile(MODEL_ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(LOCAL_MODEL_DIR)

        print("✅ Model extraction successful.")
        cache_manager.update_cache_info("audio")
        return True

    except Exception as e:
        print(f"❌ Failed to setup audio model: {e}")
        return False


# Download and extract model if needed
if not download_and_extract_model():
    raise RuntimeError("Audio model setup failed.")


# Load model and processor
processor = WhisperProcessor.from_pretrained(LOCAL_MODEL_DIR, use_fast=False)
model = WhisperForConditionalGeneration.from_pretrained(LOCAL_MODEL_DIR)


def process_audio_file(audio_path):
    """Transcribes audio using Whisper"""
    if not os.path.exists(audio_path):
        return "[Error] Audio file not found."

    waveform, sr = librosa.load(audio_path, sr=16000, mono=True)
    inputs = processor(audio=waveform, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        generated_ids = model.generate(inputs["input_features"])
        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return caption


def cleanup_session():
    """Clean up temporary files and old cache"""
    cache_manager.cleanup_old_cache()
    cache_manager.cleanup_temp_directories()
    print("🧹 Session cleanup completed")


if __name__ == "__main__":
    try:
        audio_path = "test_files/03-02-13-01-01-110-02-02-02-13.wav"  # Replace with your test file
        result = process_audio_file(audio_path)
        print("🗣️ Audio Caption:", result)

        from model_cache_manager import print_cache_stats

        print_cache_stats()

    finally:
        cleanup_session()
