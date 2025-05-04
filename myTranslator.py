# google translator from deep translator for convert text into appropriate language text
# speech recognition for convert audio speech into text format
# PyAudio
# gTTS(google text to speech) for converting the text into speech
# playsound for play that speech

# Force UTF-8 encoding when printing
import sys
sys.stdout.reconfigure(encoding='utf-8')

from deep_translator import GoogleTranslator
import speech_recognition
import gtts
import playsound

recognizer = speech_recognition.Recognizer()    
with speech_recognition.Microphone() as source:
    print('speak now')
    voice = recognizer.listen(source)
    text = recognizer.recognize_google(voice,language='en')
    print(text)

translator = GoogleTranslator(source='en', target='ur')
translation = translator.translate(text)

print(f"Translated Text: {translation}")

converted_voice = gtts.gTTS(translation, lang='ur')
converted_voice.save('voice.mp3')
playsound.playsound('voice.mp3')
