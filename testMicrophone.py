import sys
sys.stdout.reconfigure(encoding='utf-8')


import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 400  # Low threshold fix
recognizer.dynamic_energy_threshold = False  # Auto adjust disable

with sr.Microphone(device_index=1) as source:  # Apna device_index set karein
    print("🎤 Speak now...")
    recognizer.adjust_for_ambient_noise(source, duration=1)  # Noise adjust karega
    try:
        audio = recognizer.listen(source, timeout=5)
        print("✅ Voice detected!")

    except sr.WaitTimeoutError:
        print("❌ No speech detected! Try again.")
