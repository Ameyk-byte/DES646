import os
import subprocess
import eel
from asyncio import run
from dotenv import dotenv_values

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IoT import iot
from Backend.ImageGenration import GenerateImage
from Backend.Learning import run as LearningRecommender   

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Initialize UI
eel.init("web")

def ShowTextToScreen(text):
    print(text)
    eel.updateScreenText(text)

Functions = [
    "open", "close", "play", "system", "content",
    "google search", "youtube search", "iot", "LearningRecommender"
]

def SetAssistantStatus(status):
    print(f"Assistant Status: {status}")
    eel.updateStatus(status)

def QueryModifier(query):
    return query.strip()

@eel.expose
def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    Text = SpeechRecognition()
    print(f"Recognized Text: {Text}")

    if Text and "neuro" in Text.lower():
        Query = Text.lower().replace("neuro", "").strip()
        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Thinking...")

        try:
            Decision = FirstLayerDMM(Query)
            print(f"Decision: {Decision}")

            G = any(i.startswith("general") for i in Decision)
            R = any(i.startswith("realtime") for i in Decision)

            MergedQuery = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )

            # Learning Recommender Integration
            for d in Decision:
                if d.startswith("LearningRecommender"):
                    topic = d.replace("LearningRecommender", "").strip()
                    SetAssistantStatus("Preparing learning recommendations...")

                    text, payload = LearningRecommender(topic)

                    ShowTextToScreen(f"{Assistantname}: {text}")
                    TextToSpeech(text)

                    # UPDATE UI
                    if payload and "recommendations" in payload:
                        eel.updateLearningResources(payload["recommendations"])

                    return True

            # Detect image generation
            for d in Decision:
                if d.startswith("generate image"):
                    ImageGenerationQuery = d.replace("generate image ", "")
                    ImageExecution = True

            # Automation tasks
            for d in Decision:
                if any(d.startswith(func) for func in Functions) and not d.startswith("LearningRecommender"):
                    run(Automation(Decision))
                    ShowTextToScreen(f"{Assistantname}: Task executed successfully.")
                    TextToSpeech("Task executed successfully.")
                    return True

            # Image output
            if ImageExecution:
                try:
                    GenerateImage(ImageGenerationQuery)
                    ShowTextToScreen(f"{Assistantname}: Image generated successfully!")
                    TextToSpeech("Image generated successfully.")
                except:
                    ShowTextToScreen(f"{Assistantname}: Error generating image.")
                    TextToSpeech("Error generating image.")
                return True

            # Realtime queries
            if R:
                SetAssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(MergedQuery))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                TextToSpeech(Answer)
                return True

            # General responses
            if G:
                Answer = ChatBot(QueryModifier(Query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                TextToSpeech(Answer)
                return True

            # Exit
            for d in Decision:
                if d.startswith("exit"):
                    TextToSpeech("Goodbye")
                    os._exit(1)

        except Exception as e:
            print("ERROR:", e)
            ShowTextToScreen(f"{Assistantname}: Something went wrong.")
            TextToSpeech("Something went wrong.")

    else:
        print("Wake word not detected.")

# start UI + speech loop
if __name__ == "__main__":
    eel.start("index.html", size=(1024, 768), mode="chrome", block=False)
    while True:
        MainExecution()

