from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IoT import iot
from dotenv import dotenv_values
from asyncio import run
from Backend.ImageGenration import GenerateImage
import os
import subprocess

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")  # Default to "User" if not specified
Assistantname = env_vars.get("Assistantname", "Assistant")  # Default to "Assistant" if not specified

# Function to display text on the screen (replace with GUI logic if needed)
def ShowTextToScreen(text):
    """Display text on the screen."""
    print(text)

# List of supported functions
Functions = ['open', 'close', 'play', "system", "content", "google search", "youtube search", "iot"]

def SetAssistantStatus(status):
    """Set the assistant's status (replace with GUI logic if needed)."""
    print(f"Assistant Status: {status}")

def QueryModifier(query):
    """Modify the query for better processing."""
    return query.strip()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    # Perform speech recognition
    Text = SpeechRecognition()
    print(f"Recognized Text: {Text}")  # Debugging line

    # Initialize Query with a default value
    Query = ""
    
    # Check if "hello" is in the recognized text
    if Text and "neuro" in Text.lower():
        Query = Text.lower().replace("neuro", "").strip()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking...")

        try:
            # Pass the query (without "hello") to the Decision-Making Model
            Decision = FirstLayerDMM(Query)
            print(f"Decision: {Decision}")

            # Check for general and realtime queries
            G = any(i.startswith("general") for i in Decision)
            R = any(i.startswith("realtime") for i in Decision)
            MergedQuery = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )

            # Handle image generation queries
            for query in Decision:
                if query.startswith("generate image"):
                    ImageGenerationQuery = query.replace("generate image ", "")
                    ImageExecution = True

            # Handle automation tasks
            for query in Decision:
                if not TaskExecution:
                    if any(query.startswith(func) for func in Functions):
                        # Attempt to execute the automation task
                        run(Automation(Decision))
                        TaskExecution = True
                        ScreenFeedback = f"{Assistantname}: The app has been opened successfully. Please check it out!"
                        SpokenFeedback = "The app has been opened successfully. Please check it out!"
                        ShowTextToScreen(ScreenFeedback)
                        TextToSpeech(SpokenFeedback)

            # Start image generation process if required
            if ImageExecution:
                try:
                    GenerateImage(ImageGenerationQuery)  # Call the GenerateImage function
                    print("ImageGeneration.py started.")
                    ScreenFeedback = f"{Assistantname}: The image has been generated successfully. Please check it on the screen!"
                    SpokenFeedback = "The image has been generated successfully. Please check it on the screen!"
                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)
                except Exception as e:
                    print(f"Error starting ImageGeneration.py: {e}")
                    ScreenFeedback = f"{Assistantname}: Sorry, I encountered an issue while generating the image. Please try again later."
                    SpokenFeedback = "Sorry, I encountered an issue while generating the image. Please try again later."
                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)

            # Handle general and realtime queries
            if G and R or R:
                SetAssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(MergedQuery))
                ScreenFeedback = f"{Assistantname}: {Answer}"
                SpokenFeedback = Answer
                ShowTextToScreen(ScreenFeedback)
                SetAssistantStatus("Answering...")
                TextToSpeech(SpokenFeedback)
                return True

            else:
                for query in Decision:
                    if query.startswith("general"):
                        SetAssistantStatus("Thinking...")
                        QueryFinal = Query.replace("general ", "")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ScreenFeedback = f"{Assistantname}: {Answer}"
                        SpokenFeedback = Answer
                        ShowTextToScreen(ScreenFeedback)
                        SetAssistantStatus("Answering...")
                        TextToSpeech(SpokenFeedback)
                        return True

                    elif query.startswith("realtime"):
                        SetAssistantStatus("Searching...")
                        QueryFinal = Query.replace("realtime ", "")
                        Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                        ScreenFeedback = f"{Assistantname}: {Answer}"
                        SpokenFeedback = Answer
                        ShowTextToScreen(ScreenFeedback)
                        SetAssistantStatus("Answering...")
                        TextToSpeech(SpokenFeedback)
                        return True

                    elif query.startswith("exit"):
                        QueryFinal = "Okay, Bye!"
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ScreenFeedback = f"{Assistantname}: {Answer}"
                        SpokenFeedback = Answer
                        ShowTextToScreen(ScreenFeedback)
                        SetAssistantStatus("Answering...")
                        TextToSpeech(SpokenFeedback)
                        SetAssistantStatus("Exiting...")
                        os._exit(1)

                    elif query.startswith("iot"):
                        SetAssistantStatus("switching...")

                        # Extract the query after "iot " and clean it
                        QueryFinal = query.replace("iot ", "").strip()  # Remove "iot " prefix and strip whitespace
                        print(f"Cleaned Query for IoT: {QueryFinal}")  # Debug log

                        # Pass the cleaned query to the iot function
                        Answer = iot(QueryFinal)

                        # Prepare feedback for the user
                        ScreenFeedback = f"{Assistantname}: {Answer}"
                        SpokenFeedback = Answer

                        # Display and speak the feedback
                        ShowTextToScreen(ScreenFeedback)
                        SetAssistantStatus("Answering...")
                        TextToSpeech(SpokenFeedback)

                return True

        except Exception as e:
            print(f"Error during execution: {e}")
            ScreenFeedback = f"{Assistantname}: An error occurred while processing your request. Please try again."
            SpokenFeedback = "An error occurred while processing your request. Please try again."
            ShowTextToScreen(ScreenFeedback)
            TextToSpeech(SpokenFeedback)

    else:
        # If "hello" is not detected, skip the response and wait for the next input
        print("Skipping response: 'Neuro' not detected in input.")
        return

if __name__ == "__main__":
    
    while True:
        MainExecution()