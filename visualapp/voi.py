import os
import pyaudio
import wave
import time
from groq import Groq
import pygame

# === Setup Groq client ===
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY environment variable not set.")

client = Groq(api_key=api_key)

# === Generate Greeting Speech ===
speech_text = "Hello, I am VisualAid,your all in one ai assistant."
model = "playai-tts"
voice = "Fritz-PlayAI"
response_format = "mp3"  # Change to mp3
speech_file_path = "visualaid_greeting.mp3"

print("🔊 Generating greeting voice...")

response = client.audio.speech.create(
    model=model,
    voice=voice,
    input=speech_text,
    response_format=response_format
)

response.write_to_file(speech_file_path)
print(f"✅ Greeting saved as {speech_file_path}")

# === Play audio using pygame ===
try:
    pygame.mixer.init()  # Initialize the mixer module
    pygame.mixer.music.load(speech_file_path)  # Load the MP3 file
    pygame.mixer.music.play()  # Play the audio
    while pygame.mixer.music.get_busy():  # Wait for playback to finish
        pygame.time.Clock().tick(10)
except Exception as e:
    print(f"Error playing audio: {e}")

# === Audio Recording Parameters ===
CHUNK_DURATION = 15  # seconds
CHUNK_FILENAME = "chunk.wav"

# === Function to Record Audio Chunk ===
def record_chunk(filename, duration=CHUNK_DURATION):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate,
                    input=True, frames_per_buffer=chunk)

    print(f"🎙️ Listening for {duration} seconds...")
    frames = []

    for _ in range(int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# === Function to Transcribe Audio Chunk Using Groq ===
def transcribe_chunk(filename):
    with open(filename, "rb") as file:
        result = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en"
        )
    return result

# === Loop to Continuously Transcribe Audio in Real Time ===
def live_transcription():
    print("🔄 Starting live transcription... Press Ctrl+C to stop.")
    try:
        while True:
            record_chunk(CHUNK_FILENAME)
            text = transcribe_chunk(CHUNK_FILENAME)
            print(f"📝 {time.strftime('%H:%M:%S')} → {text.strip()}\n")
    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped.")

# === Entry Point ===
if __name__ == "__main__":
    live_transcription()
