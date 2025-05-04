import os
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
import ffmpeg

# Function to extract audio from video
def extract_audio_from_video(video_file):
    print("Extracting audio from video...")
    audio_file = "audio.wav"
    ffmpeg.input(video_file).output(audio_file).run()
    print("Audio extracted successfully.")
    return audio_file

# Function to preprocess audio
def preprocess_audio(audio_file):
    print("Preprocessing the audio...")
    # Load the audio file
    audio = AudioSegment.from_wav(audio_file)
    
    # Apply noise reduction (can be done using pydub or other noise reduction libraries)
    # In this case, we'll just reduce the volume to simulate preprocessing
    audio = audio - 10  # Reduce the volume by 10dB
    
    # Save the cleaned audio
    cleaned_audio_file = "cleaned_audio.wav"
    audio.export(cleaned_audio_file, format="wav")
    print("Noise reduction applied and audio saved as cleaned_audio.wav.")
    return cleaned_audio_file

# Function to perform speech recognition
def recognize_speech_from_audio(audio_file):
    print("Performing speech recognition...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Record the audio from the file
    try:
        # Recognize speech using Google Speech Recognition API
        recognized_text = recognizer.recognize_google(audio)
        print(f"Recognized text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function to translate text to Urdu
def translate_to_urdu(text):
    print("Translating text to Urdu...")
    translator = Translator()
    try:
        # Translate text to Urdu
        translated_text = translator.translate(text, dest='ur').text
        translated_text = translated_text.encode('utf-8').decode('utf-8')  # Ensure UTF-8 encoding
        print(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        return None

# Main function to run the process
def main(video_file):
    # Step 1: Extract audio from video
    audio_file = extract_audio_from_video(video_file)
    
    # Step 2: Preprocess the audio
    cleaned_audio_file = preprocess_audio(audio_file)
    
    # Step 3: Perform speech recognition
    recognized_text = recognize_speech_from_audio(cleaned_audio_file)
    if recognized_text:
        # Step 4: Translate the recognized text to Urdu
        translated_text = translate_to_urdu(recognized_text)
        if translated_text:
            print("Final translated text:", translated_text)

# Run the main function with the video file as input
if __name__ == "__main__":
    video_file = "test.mp4"  # Replace with your video file path
    main(video_file)
