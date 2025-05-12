import os
from pydub import AudioSegment
import speech_recognition as sr
from deep_translator import GoogleTranslator
import ffmpeg
import sys
import gtts
from dotenv import load_dotenv
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog
import librosa
import numpy as np

# Load environment variables
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
sys.stdout.reconfigure(encoding='utf-8')

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
        audio = audio - 10  # Basic noise reduction
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

def detect_gender_with_librosa(audio_file):
    print("Detecting speaker gender using pitch analysis...")

    try:
        # Load the audio file
        # y: audio waveform (numpy array of amplitudes)
        # sr_rate: sample rate of the audio (samples per second)
        y, sr_rate = librosa.load(audio_file, sr=None)

        # Use librosa's pyin to estimate pitch (f0) over time
        # f0: fundamental frequency array (NaN where pitch not detected)
        # voiced_flag: boolean array indicating voiced regions
        # voiced_probs: probability of a region being voiced
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=75, fmax=300)

        # Remove undefined (NaN) pitch values
        f0 = f0[~np.isnan(f0)]

        # If no pitch detected (e.g., silence or noise), default to "male"
        if len(f0) == 0:
            print("No pitch detected, defaulting to male.")
            return "male"

        # Compute the average pitch from the valid pitch values
        avg_pitch = np.mean(f0)
        print(f"Average pitch: {avg_pitch:.2f} Hz")

        # Classify based on average pitch thresholds
        if avg_pitch < 165:
            return "male"        # Typical male pitch range
        elif avg_pitch < 250:
            return "female"      # Typical female pitch range
        else:
            return "child"       # Higher pitch suggests a child's voice

    except Exception as e:
        # Handle unexpected errors gracefully
        print(f"Error detecting gender: {e}")
        return "male"  # Default fallback

def speak_translation(text, gender='male'):
    try:
        # Choose the TLD (Top-Level Domain) based on gender
        # 'co.in' for male and 'com.pk' for female (this impacts the accent/tone slightly)
        tld = 'co.in' if gender == 'male' else 'com.pk'  

        # Use gTTS (Google Text-to-Speech) to convert the text into speech
        # lang='ur' specifies that the speech will be in Urdu
        # tld specifies the regional accent/tone based on gender
        converted_voice = gtts.gTTS(text, lang='ur', tld=tld)

        # Save the converted voice to an MP3 file ('voice.mp3')
        converted_voice.save('voice.mp3')
        
    except Exception as e:
        # Handle any errors that occur during the TTS process
        print(f"Error in text-to-speech: {e}")


def ffmpeg_speedup(input_file: str, output_file: str, speed: float = 1.5):
    ffmpeg.input(input_file).output(output_file, **{'filter:a': f"atempo={speed}"}).run(overwrite_output=True)

def patch_audio_to_video(input_video: str, new_audio: str, output_video: str):
    try:
        # Load the input video using ffmpeg
        # `video_input` will hold the video stream from the input file
        video_input = ffmpeg.input(input_video)
        
        # Load the new audio file using ffmpeg
        # `audio_input` will hold the audio stream from the new audio file
        audio_input = ffmpeg.input(new_audio)
        
        # Use ffmpeg to output the patched video with the new audio
        ffmpeg.output(
            video_input.video,   # Use the video stream from the input video
            audio_input.audio,   # Use the audio stream from the new audio file
            output_video,        # Specify the name of the output video file
            vcodec='copy',       # Copy the video codec (no re-encoding of video)
            acodec='aac',        # Use the AAC audio codec for the new audio
            shortest=None        # Ensure the output video stops at the shorter stream's length (video or audio)
        ).global_args('-map', '0:v:0', '-map', '1:a:0').run(overwrite_output=True)
        # Map the video and audio streams correctly
          # Execute the command, allowing overwriting of the output file if it exists
        
        # Print a success message
        print(f"Patched video saved as: {output_video}")
    
    except Exception as e:
        # Handle any errors that may occur during the patching process
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
                    gender = detect_gender_with_librosa(cleaned_audio_file)
                    print(f"Detected Gender: {gender}")
                    speak_translation(cleaned_urdu, gender=gender)
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

def select_video_file():
    root = tk.Tk()
    root.withdraw()
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
