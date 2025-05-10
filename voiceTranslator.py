import os
from pydub import AudioSegment
import speech_recognition as sr
from deep_translator import GoogleTranslator
import ffmpeg
import sys
import gtts
import playsound
# from openai import OpenAI           # new client class :contentReference[oaicite:6]{index=6}

# Load variables from `.env` into os.environ
# load_dotenv()  # reads .env in current working directory :contentReference[oaicite:5]{index=5}
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
import os

# Create a Gemini client using your API key
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])  # Gemini Developer API mode :contentReference[oaicite:6]{index=6}

def refine_urdu_gemini(english: str, literal_urdu: str) -> str:
    """
    Send English + literal Urdu to Gemini, return idiomatic Urdu.
    """
    # Build the prompt merging both inputs
    prompt = (
        f"You are a professional Urdu editor.\n"
        f"English: \"{english}\"\n"
        f"Literal Urdu: \"{literal_urdu}\"\n\n"
        "Please rewrite the Literal Urdu translation so it reads naturally in Urdu, "
        "using proper grammar and idiomatic expressions. Only return the improved Urdu."
    )
    # Call Gemini's generate_content endpoint
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",     # latest Flash model :contentReference[oaicite:7]{index=7}
        contents=prompt,                  # prompt text :contentReference[oaicite:8]{index=8}
        config=types.GenerateContentConfig(
            temperature=0.7,              # moderate creativity :contentReference[oaicite:9]{index=9}
            max_output_tokens=300         # max tokens in reply :contentReference[oaicite:10]{index=10}
        )
    )
    # Return only the cleaned‑up Urdu text
    return response.text.strip()



# Force the output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Function to extract audio from video
def extract_audio_from_video(video_file):
    print(" Extracting audio from video...")
    audio_file = "audio.wav"
    ffmpeg.input(video_file).output(audio_file, vn=None).run()
    print(" Audio extracted successfully.")
    return audio_file

# Function to preprocess audio
def preprocess_audio(audio_file):
    print(" Preprocessing the audio...")
    try:
        audio = AudioSegment.from_wav(audio_file)
        audio = audio - 10  # Simulate noise reduction
        cleaned_audio_file = "cleaned_audio.wav"
        audio.export(cleaned_audio_file, format="wav")
        print(" Noise reduction applied.")
        return cleaned_audio_file
    except Exception as e:
        print(f" Error during audio preprocessing: {e}")
        return None

# Function to perform speech recognition
def recognize_speech_from_audio(audio_file):
    print(" Performing speech recognition...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio)
        print(f" Recognized text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        print(" Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f" API Request Error: {e}")
        return None

# Function to translate text to Urdu
def translate_to_urdu(text):
    print(" Translating text to Urdu...")
    try:
        translated_text = GoogleTranslator(source='auto', target='ur').translate(text)
        print(f" Translated text: {translated_text}")

        # Save translation
        with open('translated_text.txt', 'w', encoding='utf-8') as file:
            file.write(translated_text)
        
        return translated_text
    except Exception as e:
        print(f" Translation error: {e}")
        return None

# Function to convert Urdu text to speech
def speak_translation(text):
    try:
        converted_voice = gtts.gTTS(text, lang='ur')
        converted_voice.save('voice.mp3')
        # playsound.playsound('voice.mp3')
    except Exception as e:
        print(f" Error in text-to-speech: {e}")

# Main process pipeline
def main(video_file):
    audio_file = extract_audio_from_video(video_file)
    cleaned_audio_file = preprocess_audio(audio_file)
    if cleaned_audio_file:
        recognized_text = recognize_speech_from_audio(cleaned_audio_file)
        if recognized_text:
            translated_text = translate_to_urdu(recognized_text)
            if translated_text:
                # Get a more natural Urdu version via ChatGPT
                cleaned_urdu = refine_urdu_gemini(recognized_text, translated_text)
                print("Cleaned Urdu:", cleaned_urdu)
                speak_translation(cleaned_urdu)
                # print(" Final Translated Text:", translated_text)
                # speak_translation(translated_text)

                # Use cleaned_urdu (instead of translated_text) for TTS
                # speak_translation(cleaned_urdu)
            else:
                print(" Translation failed.")
        else:
            print(" No recognized text to translate.")
    else:
        print(" Audio preprocessing failed.")

def patch_audio_to_video(input_video: str, new_audio: str, output_video: str):
    """
    Replace the audio track of `input_video` with `new_audio`,
    writing the result to `output_video`.
    """
    # Load inputs
    video_input = ffmpeg.input(input_video)
    audio_input = ffmpeg.input(new_audio)
    
    # Build output: copy video, encode audio to AAC, end at shorter stream
    (
        ffmpeg
        .output(
            video_input.video,      # video stream
            audio_input.audio,      # audio stream
            output_video,
            vcodec='copy',          # stream‑copy video
            acodec='aac',           # encode audio
            shortest=None           # -shortest flag
        )
        .global_args(
            '-map', '0:v:0',        # map video from first input
            '-map', '1:a:0'         # map audio from second input
        )
        .run(overwrite_output=True)
    )
    print(f"Patched video saved as: {output_video}")


if __name__ == "__main__":
    video_file = r"20-second English Reading.mp4"
    main(video_file)
    patch_audio_to_video("20-second English Reading.mp4", "voice.mp3", "test_urdu.mp4")