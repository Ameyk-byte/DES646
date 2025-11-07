from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IoT import iot
from Backend.ImageGenration import GenerateImage
from Backend.Learning import run as LearningRecommender  # ✅ NEW
from dotenv import dotenv_values
from asyncio import run
import os
import subprocess

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

def ShowTextToScreen(text):
    print(text)

# Add LearningRecommender in supported functions
Functions = ['open', 'close', 'play', "system", "content",
             "google search", "youtube search", "iot", "LearningRecommender"]  # ✅ UPDATED

def SetAssistantStatus(status):
    print(f"Assistant Status: {status}")

def QueryModifier(query):
    return query.strip()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    # Speech → text
    Text = SpeechRecognition()
    print(f"Recognized Text: {Text}")

    Query = ""

    # wake word: neuro
    if Text and "neuro" in Text.lower():
        Query = Text.lower().replace("neuro", "").strip()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking...")

        try:
            Decision = FirstLayerDMM(Query)
            print(f"Decision: {Decision}")

            G = any(i.startswith("general") for i in Decision)
            R = any(i.startswith("realtime") for i in Decision)

            MergedQuery = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )

            # Detect image generation
            for d in Decision:
                if d.startswith("generate image"):
                    ImageGenerationQuery = d.replace("generate image ", "")
                    ImageExecution = True

            # ✅ Detect LearningRecommender intent
            for d in Decision:
                if d.startswith("LearningRecommender"):
                    topic = d.replace("LearningRecommender", "").strip()
                    SetAssistantStatus("Preparing learning recommendations...")

                    # Call recommender
                    text, payload = LearningRecommender(Query)

                    ScreenFeedback = f"{Assistantname}: {text}"
                    SpokenFeedback = "Here are some learning resources I recommend."

                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)

                    # Optional print recommended items to console
                    if payload and "recommendations" in payload:
                        for r in payload["recommendations"]:
                            print(f"- {r['title']} ({r['type']})")

                    return True

            # Handle automation tasks
            for d in Decision:
                if any(d.startswith(func) for func in Functions) and not d.startswith("LearningRecommender"):
                    run(Automation(Decision))
                    TaskExecution = True
                    ScreenFeedback = f"{Assistantname}: Task executed successfully."
                    SpokenFeedback = "Task executed successfully."
                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)

            # Image generation execution
            if ImageExecution:
                try:
                    GenerateImage(ImageGenerationQuery)
                    ScreenFeedback = f"{Assistantname}: The image has been generated successfully!"
                    SpokenFeedback = "Image generated successfully."
                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)
                except Exception as e:
                    print(f"Error: {e}")
                    ShowTextToScreen(f"{Assistantname}: Error generating image.")
                    TextToSpeech("Sorry, I had an issue generating image.")

            # realtime search
            if R:
                SetAssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(MergedQuery))
                ScreenFeedback = f"{Assistantname}: {Answer}"
                SpokenFeedback = Answer
                ShowTextToScreen(ScreenFeedback)
                SetAssistantStatus("Answering...")
                TextToSpeech(SpokenFeedback)
                return True

            # general chatbot
            if G:
                SetAssistantStatus("Thinking...")
                QueryFinal = Query.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ScreenFeedback = f"{Assistantname}: {Answer}"
                SpokenFeedback = Answer
                ShowTextToScreen(ScreenFeedback)
                SetAssistantStatus("Answering...")
                TextToSpeech(SpokenFeedback)
                return True

            # exit
            for d in Decision:
                if d.startswith("exit"):
                    QueryFinal = "Okay, bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    TextToSpeech(Answer)
                    os._exit(1)

            # IoT
            for d in Decision:
                if d.startswith("iot"):
                    SetAssistantStatus("Switching...")
                    QueryFinal = d.replace("iot ", "")
                    Answer = iot(QueryFinal)
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    TextToSpeech(Answer)
                    return True

        except Exception as e:
            print(f"Error: {e}")
            ShowTextToScreen(f"{Assistantname}: Something went wrong.")
            TextToSpeech("Sorry, something went wrong.")

    else:
        print("Skipping: wake word not detected.")
        return

if __name__ == "__main__":
    while True:
        MainExecution()
