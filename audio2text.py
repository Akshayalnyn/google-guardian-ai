import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import os

# Use Hugging Face model directly
MODEL_NAME = (
    "MU-NLPC/whisper-tiny-audio-captioning"  # Latest and highest quality Whisper model
)
CACHE_DIR = "audio_models_cache"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_whisper_model():
    """Load the Whisper model from Hugging Face cache or download if needed."""
    try:
        print("🔄 Loading Whisper model...")

        # Create cache directory if it doesn't exist
        os.makedirs(CACHE_DIR, exist_ok=True)

        # Load from Hugging Face (will download if not cached, load from cache if available)
        print(f"📦 Loading {MODEL_NAME}...")
        processor = WhisperProcessor.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
        model = WhisperForConditionalGeneration.from_pretrained(
            MODEL_NAME, cache_dir=CACHE_DIR
        ).to(device)

        print("✅ Whisper model loaded successfully!")
        return processor, model

    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        print("💡 Make sure you have internet connection for first-time download")
        exit(1)


# Load model and processor
processor, model = load_whisper_model()


def process_audio_file(audio_path):
    """Transcribes audio using Whisper"""
    if not os.path.exists(audio_path):
        return "[Error] Audio file not found."

    try:
        # Load and preprocess audio
        waveform, sr = librosa.load(audio_path, sr=16000, mono=True)

        # Limit audio length to prevent memory issues (30 seconds max)
        max_length = 30 * 16000  # 30 seconds at 16kHz
        if len(waveform) > max_length:
            waveform = waveform[:max_length]
            print(f"⚠️ Audio truncated to 30 seconds for processing")

        # Process audio with proper parameters
        inputs = processor(
            audio=waveform,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True,
        )

        # Move inputs to device
        input_features = inputs["input_features"].to(device)

        # Generate transcription with forced decoder input ids
        with torch.no_grad():
            # Create proper decoder input ids for Whisper
            forced_decoder_ids = processor.get_decoder_prompt_ids(
                language="en", task="transcribe"
            )

            generated_ids = model.generate(
                input_features,
                forced_decoder_ids=forced_decoder_ids,
                max_length=448,
                num_beams=1,  # Use greedy decoding for tiny model
                do_sample=False,
                early_stopping=True,
                suppress_tokens=[],  # Don't suppress any tokens
            )

            # Decode the transcription
            transcription = processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]

        # Clean up the transcription
        transcription = transcription.strip()

        # Check for repetitive output (like long sequences of same characters)
        if len(transcription) > 100 and len(set(transcription.replace(" ", ""))) < 5:
            return "[Warning] Audio may be unclear - detected repetitive transcription pattern"

        return transcription if transcription else "[No speech detected]"

    except Exception as e:
        return f"[Error] Audio processing failed: {e}"


if __name__ == "__main__":
    print("🎙️ Guardian AI — Audio-to-Text (Whisper)")

    # Test with the provided test file
    test_audio_path = "test_files/03-02-13-01-01-110-02-02-02-13.wav"

    if os.path.exists(test_audio_path):
        print(f"🔊 Processing: {test_audio_path}")
        result = process_audio_file(test_audio_path)
        print(f"🗣️ Transcription: {result}")
    else:
        print(f"⚠️ Test file not found: {test_audio_path}")
        audio_path = input("Enter path to audio file: ").strip()
        if audio_path:
            result = process_audio_file(audio_path)
            print(f"🗣️ Transcription: {result}")
