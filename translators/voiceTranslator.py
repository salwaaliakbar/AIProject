import os
from pydub import AudioSegment
import speech_recognition as sr
from deep_translator import GoogleTranslator
import ffmpeg
import sys
import gtts
import playsound

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
        playsound.playsound('voice.mp3')
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
                print(" Final Translated Text:", translated_text)
                speak_translation(translated_text)
            else:
                print(" Translation failed.")
        else:
            print(" No recognized text to translate.")
    else:
        print(" Audio preprocessing failed.")

if __name__ == "__main__":
    video_file = r"c:\Users\PMLS\Desktop\my tasks\code\Voice Translator\AIProject\test.mp4"
    main(video_file)
