import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import os

# Load model and processor
model_path = os.path.join(os.path.dirname(__file__), "audio_models")
processor = WhisperProcessor.from_pretrained(model_path, use_fast=False)
model = WhisperForConditionalGeneration.from_pretrained(model_path)


# Example usage function
def process_audio_file(audio_path):
    """Process an audio file and return its caption"""
    waveform, sr = librosa.load(audio_path, sr=16000, mono=True)

    # Generate caption
    inputs = processor(audio=waveform, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        generated_ids = model.generate(inputs["input_features"])
        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return caption


# Example usage (only runs if this file is executed directly)
if __name__ == "__main__":
    # audio_path = "path/to/your/audio/file.mp3"  # Update this path as needed
    # caption = process_audio_file(audio_path)
    # print("🗣️ Audio Caption:", caption)
    print(
        "Audio processing module loaded. Use process_audio_file(path) to process audio files."
    )
