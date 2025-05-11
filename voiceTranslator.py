import os
from pydub import AudioSegment
import speech_recognition as sr
from deep_translator import GoogleTranslator
import ffmpeg
import sys
import gtts
import playsound
from dotenv import load_dotenv
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def refine_urdu_gemini(english: str, literal_urdu: str) -> str:
    prompt = (
        f"You are a professional Urdu editor.\n"
        f"English: \"{english}\"\n"
        f"Literal Urdu: \"{literal_urdu}\"\n\n"
        "Please rewrite the Literal Urdu translation so it reads naturally in Urdu, "
        "using proper grammar and idiomatic expressions. Only return the improved Urdu."
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=300
        )
    )
    return response.text.strip()

sys.stdout.reconfigure(encoding='utf-8')

def extract_audio_from_video(video_file):
    print("Extracting audio from video...")
    audio_file = "audio.wav"
    try:
        ffmpeg.input(video_file).output(audio_file, vn=None).run()
        print("Audio extracted successfully.")
        return audio_file
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def preprocess_audio(audio_file):
    print("Preprocessing the audio...")
    try:
        audio = AudioSegment.from_wav(audio_file)
        audio = audio - 10  # Simulate noise reduction
        cleaned_audio_file = "cleaned_audio.wav"
        audio.export(cleaned_audio_file, format="wav")
        print("Noise reduction applied.")
        return cleaned_audio_file
    except Exception as e:
        print(f"Error during audio preprocessing: {e}")
        return None

def recognize_speech_from_audio(audio_file):
    print("Performing speech recognition...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio)
        print(f"Recognized text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"API Request Error: {e}")
        return None

def translate_to_urdu(text):
    print("Translating text to Urdu...")
    try:
        translated_text = GoogleTranslator(source='auto', target='ur').translate(text)
        print(f"Translated text: {translated_text}")
        with open('translated_text.txt', 'w', encoding='utf-8') as file:
            file.write(translated_text)
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def speak_translation(text):
    try:
        converted_voice = gtts.gTTS(text, lang='ur')
        converted_voice.save('voice.mp3')
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        print(f" Error in text-to-speech: {e}")

def ffmpeg_speedup(input_file: str, output_file: str, speed: float = 1.5):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, **{'filter:a': f"atempo={speed}"})
        .run(overwrite_output=True)
    )


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
    try:
        video_input = ffmpeg.input(input_video)
        audio_input = ffmpeg.input(new_audio)
        ffmpeg.output(
            video_input.video, audio_input.audio, output_video,
            vcodec='copy', acodec='aac', shortest=None
        ).global_args('-map', '0:v:0', '-map', '1:a:0').run(overwrite_output=True)
        print(f"Patched video saved as: {output_video}")
    except Exception as e:
        print(f"Error while patching video: {e}")

def main(video_file):
    audio_file = extract_audio_from_video(video_file)
    if audio_file:
        cleaned_audio_file = preprocess_audio(audio_file)
        if cleaned_audio_file:
            recognized_text = recognize_speech_from_audio(cleaned_audio_file)
            if recognized_text:
                translated_text = translate_to_urdu(recognized_text)
                if translated_text:
                    cleaned_urdu = refine_urdu_gemini(recognized_text, translated_text)
                    print("Cleaned Urdu:", cleaned_urdu)
                    speak_translation(cleaned_urdu)
                    ffmpeg_speedup('voice.mp3', 'voice_fast.mp3', speed=2.0)
                    patch_audio_to_video(video_file, "voice_fast.mp3", "test_urdu.mp4")
                else:
                    print("Translation failed.")
            else:
                print("No recognized text to translate.")
        else:
            print("Audio preprocessing failed.")
    else:
        print("Audio extraction failed.")

# use tkinter library for select vedio file

def select_video_file():
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter root window

    video_file = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
    )

    if video_file:
        print(f"Selected video file: {video_file}")
        main(video_file)
    else:
        print("No video file selected.")

if __name__ == "__main__":
    select_video_file()

