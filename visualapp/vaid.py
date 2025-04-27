import streamlit as st
import os
import threading
import time
import pygame
import pyttsx3
import speech_recognition as sr
import pyautogui
import webbrowser

# === WhatsApp Automation ===
class WhatsAppAutomation:

    @staticmethod
    def open_chat(friend_name, disable_failsafe=False):
        if disable_failsafe:
            pyautogui.FAILSAFE = False

        os.system("start whatsapp:")
        time.sleep(5)

        pyautogui.typewrite(friend_name, interval=0.1)
        time.sleep(1.5)

        pyautogui.press('down')
        time.sleep(0.5)

        pyautogui.press('enter')
        time.sleep(1)

    @staticmethod
    def send_message(friend_name, message, disable_failsafe=False):
        WhatsAppAutomation.open_chat(friend_name, disable_failsafe)
        pyautogui.typewrite(message, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        print(f"Message sent to {friend_name}!")
        WhatsAppAutomation.close_whatsapp()

    @staticmethod
    def audio_call(friend_name, disable_failsafe=False):
        WhatsAppAutomation.open_chat(friend_name, disable_failsafe)
        for _ in range(11):
            pyautogui.press('tab')
            time.sleep(0.2)
        pyautogui.press('enter')
        print(f"Audio call started with {friend_name}!")

        WhatsAppAutomation.call_timer_and_end()

    @staticmethod
    def video_call(friend_name, disable_failsafe=False):
        WhatsAppAutomation.open_chat(friend_name, disable_failsafe)
        for _ in range(10):
            pyautogui.press('tab')
            time.sleep(0.2)
        pyautogui.press('enter')
        print(f"📹 Video call started with {friend_name}!")

        WhatsAppAutomation.call_timer_and_end()

    @staticmethod
    def call_timer_and_end():
        print("⏳ Waiting for 3 minutes...")
        time.sleep(180)

        response = input("Is the call completed? (yes/no): ").strip().lower()
        if response == 'yes':
            WhatsAppAutomation.cut_call()
            WhatsAppAutomation.close_whatsapp()
        else:
            print("Leaving the call running.")

    @staticmethod
    def cut_call():
        print("Ending the call")
        pyautogui.press('space')
        time.sleep(0.5)

        for _ in range(7):
            pyautogui.press('tab')
            time.sleep(0.2)

        pyautogui.press('enter')
        print("Call ended.")

    @staticmethod
    def close_whatsapp():
        pyautogui.hotkey('alt', 'f4')
        print("WhatsApp closed successfully.\n")


# === Import your modules ===
from voi import record_chunk, transcribe_chunk
from news import fetch_top_news_gnewsapi
from groq import Groq

# === Setup Groq client ===
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY environment variable not set.")

client = Groq(api_key=api_key)

# === Greeting ===
def play_greeting():
    if not os.path.exists("visualaid_greeting.mp3"):
        speech_text = "Hello, I am VisualAid, your all-in-one AI assistant."
        response = client.audio.speech.create(
            model="playai-tts",
            voice="Fritz-PlayAI",
            input=speech_text,
            response_format="mp3"
        )
        with open("visualaid_greeting.mp3", "wb") as f:
            f.write(response.content)  # Correct way to write audio data
    pygame.mixer.init()
    pygame.mixer.music.load("visualaid_greeting.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# === TTS ===
def speak_text(text):
    def tts_worker(text):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=tts_worker, args=(text,), daemon=True).start()

# === Trigger Listener ===
def listen_for_trigger(timeout=60):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    start_time = time.time()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if time.time() - start_time > timeout:
                return None
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                if "hello" in command:
                    return "hello"
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                continue
            except Exception:
                continue

# === Command Processor ===
def process_command(command):
    command = command.lower()
    whatsapp = WhatsAppAutomation()
    response = ""

    if "wifi on" in command:
        os.system('netsh interface set interface name="Wi-Fi" admin=enabled')
        response = "WiFi turned ON."

    elif "wifi off" in command:
        os.system('netsh interface set interface name="Wi-Fi" admin=disabled')
        response = "WiFi turned OFF."

    elif "volume up" in command:
        os.system("nircmd.exe changesysvolume 5000")
        response = "Volume increased."

    elif "volume down" in command:
        os.system("nircmd.exe changesysvolume -5000")
        response = "Volume decreased."

    elif "news" in command:
        news_list = fetch_top_news_gnewsapi(api_key="c9ad3127d06d959d42a75068ada89f8c", limit=5)
        response = "\n".join([f"{i+1}. {news['title']}" for i, news in enumerate(news_list)])

    elif "translate" in command:
        text_to_translate = command.replace("translate", "").strip()
        result = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": f"Translate the following English text to Hindi: {text_to_translate}"}],
        )
        response = result.choices[0].message.content.strip()

    elif "email summary" in command:
        dummy_text = "You have 2 emails: one from Amazon about your order, and one from the University about exam results."
        result = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": f"Summarize this: {dummy_text}"}],
        )
        response = result.choices[0].message.content.strip()

    elif "send message to" in command:
        contact = command.split("send message to")[-1].strip()
        whatsapp.send_message(friend_name=contact, message="Hello from VisualAid!")
        response = f"Message sent to {contact}."

    elif "voice call" in command:
        contact = command.split("voice call")[-1].strip()
        whatsapp.audio_call(friend_name=contact)
        response = f"Voice calling {contact}."

    elif "video call" in command:
        contact = command.split("video call")[-1].strip()
        whatsapp.video_call(friend_name=contact)
        response = f"Video calling {contact}."

    elif "direction to" in command:
        place = command.split("direction to")[-1].strip()
        webbrowser.open(f"https://www.google.com/maps/dir//{place.replace(' ', '+')}")
        response = f"Getting directions to {place}."

    else:
        response = "Sorry, I didn't understand the command."

    return response

# === Streamlit UI ===
st.set_page_config(page_title="VisualAid", layout="centered")
st.title("👀 VisualAid - AI Voice Assistant")

if 'greeted' not in st.session_state:
    play_greeting()
    st.session_state['greeted'] = True

st.header("🎙️ Listening for 'hello' trigger...")

trigger = listen_for_trigger()

if trigger == "hello":
    st.success("Trigger word detected! Listening for your command...")
    record_chunk("chunk.wav")
    command = transcribe_chunk("chunk.wav")

    st.info(f"Recognized Command: {command}")

    response = process_command(command)
    st.success(f"Response: {response}")

    speak_text(response)
else:
    st.warning("No trigger detected. Still listening...")
