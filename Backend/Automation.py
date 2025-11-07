from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import paho.mqtt.client as mqtt  # MQTT library for IoT
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import logging

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# User agent for Google search
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['USERNAME']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]

# HiveMQ Cloud MQTT broker details (IoT integration)
MQTT_BROKER = "04fff2a5571b47729adc6fcd76c17bd0.s1.eu.hivemq.cloud"
MQTT_PORT = 8883  # Secure MQTT port for HiveMQ Cloud

# MQTT Credentials
MQTT_USER = "hivemq.webclient.1741844782940"
MQTT_PASSWORD = "v2,7<B&k@9jKFLX8mewD"

# Base topic to publish commands
BASE_TOPIC = "esp8266/devices"

# List of devices
device_names = ["light", "light2", "fan", "fan2", "plug", "plug2", "tv", "ac", "heater", "bulb"]

# Create an MQTT client instance
mqtt_client = mqtt.Client()

# Set username and password for authentication
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Set TLS for secure connection
mqtt_client.tls_set()

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(BASE_TOPIC + "/#")  # Subscribe to all device topics
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# Assign event callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker
print("Connecting to MQTT broker...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the loop to process network traffic
mqtt_client.loop_start()

# Function to control a specific IoT device
def control_device(device_name, state):
    """
    Control a specific device by publishing a command to the MQTT broker.

    Parameters:
        device_name (str): The name of the device to control.
        state (str): The desired state of the device ("ON" or "OFF").

    Returns:
        str: A message indicating success or failure.
    """
    # Validate the device name
    if device_name not in device_names:
        logging.error(f"Invalid device name: {device_name}")
        return f"Sorry, no device available with the name '{device_name}'."

    # Validate the state
    if state.upper() not in ["ON", "OFF"]:
        logging.error(f"Invalid state: {state}")
        return "Invalid state. Please enter 'ON' or 'OFF'."

    # Create the command message
    command = f"{device_name} {state.upper()}"
    print(f"Publishing command: {command}")

    # Publish the command to the MQTT broker
    try:
        mqtt_client.publish(BASE_TOPIC, command)
        return f"Command '{command}' published successfully to topic: {BASE_TOPIC}"
    except Exception as e:
        logging.error(f"Error publishing command: {e}")
        return "An error occurred while publishing the command."

# Existing functions...

def GoogleSearch(Topic):
    """Perform a Google search."""
    try:
        search(Topic)
        return True
    except Exception as e:
        logging.error(f"Error during Google search: {e}")
        return False

def Content(Topic, output_dir="Data"):
    """Write content and open it in Notepad."""
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    file_path = rf"{output_dir}\{Topic.lower().replace(' ', '')}.txt"
    try:
        ContentByAI = ContentWriterAI(Topic)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
        OpenNotepad(file_path)
        return True
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return False

def YoutubeSearch(Topic):
    """Search on YouTube."""
    try:
        UrlSearch = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(UrlSearch)
        return True
    except Exception as e:
        logging.error(f"Error during YouTube search: {e}")
        return False

def PlayYoutube(query):
    """Play a video on YouTube."""
    try:
        playonyt(query)
        return True
    except Exception as e:
        logging.error(f"Error playing YouTube video: {e}")
        return False

def OpenApp(app, sess=requests.session()):
    """Open an application or website."""
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"OPENING {app.upper()}")
        return True
    except Exception as e:
        logging.warning(f"Error opening app: {e}")
        pass  # Ignore errors for unrecognized apps

    # Fallback URLs for popular apps
    fallback_urls = {
        "instagram": "https://www.instagram.com",
        "youtube": "https://www.youtube.com",
        "spotify": "https://open.spotify.com",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "twitch": "https://www.twitch.tv",  # Added Twitch fallback URL
        # Add more mappings as needed
    }

    # Check if the app has a fallback URL
    app_lower = app.lower()
    if app_lower in fallback_urls:
        try:
            webbrowser.open(fallback_urls[app_lower])
            print(f"OPENING {app.upper()} VIA FALLBACK URL")
            return True
        except Exception as e:
            logging.error(f"Error opening fallback URL for {app}: {e}")
            return False

    # Fallback: Search Google for the app/website
    def extract_links(html):
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        extracted_links = [link.get('href') for link in links if "http" in link.get('href')]
        logging.info(f"Extracted links from Google search: {extracted_links}")
        return extracted_links

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": useragent}
        logging.info(f"Performing Google search for query: {query}")
        response = sess.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to retrieve search results for query: {query}")
            return None

    html = search_google(app)
    if html:
        links = extract_links(html)
        if links:
            try:
                webbrowser.open(links[0])
                print(f"OPENING {app.upper()} VIA GOOGLE SEARCH")
                return True
            except Exception as e:
                logging.error(f"Error opening link from Google search: {e}")
                return False
        else:
            logging.warning("No valid links found.")
            return False
    else:
        logging.error("Failed to retrieve search results.")
        return False

def CloseApp(app):
    """Close an application."""
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        logging.warning(f"Error closing app: {e}")
        return False

def System(command):
    """Perform system actions (e.g., volume control)."""
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    def shutdown():
        os.system("shutdown /s /t 1")

    def restart():
        os.system("shutdown /r /t 1")

    def hibernate():
        os.system("shutdown /h")

    try:
        if command == "mute":
            mute()
        elif command == "unmute":
            unmute()
        elif command == "volume up":
            volume_up()
        elif command == "volume down":
            volume_down()
        elif command == "shutdown":
            shutdown()
        elif command == "restart":
            restart()
        elif command == "hibernate":
            hibernate()
        else:
            logging.warning(f"Unsupported system command: {command}")
            return False
        return True
    except Exception as e:
        logging.error(f"Error executing system command: {e}")
        return False

async def TranslateAndExecute(commands: list[str]):
    """Translate commands into executable tasks."""
    funcs = []
    for command in commands:
        if command.startswith("open"):
            app = command.removeprefix("open ").strip()
            fun = asyncio.to_thread(OpenApp, app)
            funcs.append(fun)
        elif command.startswith("close"):
            app = command.removeprefix("close ").strip()
            fun = asyncio.to_thread(CloseApp, app)
            funcs.append(fun)
        elif command.startswith("play"):
            query = command.removeprefix("play ").strip()
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)
        elif command.startswith("content"):
            topic = command.removeprefix("content ").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)
        elif command.startswith("google search"):
            topic = command.removeprefix("google search ").strip()
            fun = asyncio.to_thread(GoogleSearch, topic)
            funcs.append(fun)
        elif command.startswith("youtube search"):
            topic = command.removeprefix("youtube search ").strip()
            fun = asyncio.to_thread(YoutubeSearch, topic)
            funcs.append(fun)
        elif command.startswith("system"):
            action = command.removeprefix("system ").strip()
            fun = asyncio.to_thread(System, action)
            funcs.append(fun)
        elif command.startswith("iot"):
            parts = command.removeprefix("iot ").strip().split()
            if len(parts) == 2:
                device_name, state = parts
                fun = asyncio.to_thread(control_device, device_name, state)
                funcs.append(fun)
            else:
                logging.warning(f"Invalid IoT command: {command}")
        else:
            logging.warning(f"No function found for command: {command}")

    results = await asyncio.gather(*funcs, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logging.error(f"Task failed: {result}")
        else:
            yield result

async def Automation(commands: list[str]):
    """Execute automation tasks."""
    async for _ in TranslateAndExecute(commands):
        pass
    return True