from cohere import Client
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
co = Client(api_key=CohereAPIKey)

# Updated list of functions
funcs = [
    "exit", "general", "realtime", "open", "close", "play", "generate image",
    "system", "content", "google search", "youtube search", "reminder", "iot",
    "LearningRecommender"
]

message = []

# Updated preamble including Learning Recommender rule
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.

*** Do not answer any query, just classify it. ***

-> Respond with 'LearningRecommender (topic)' if a query asks to learn, study, find tutorials, courses, roadmaps, guides or educational resources.
Examples:
- 'recommend resources for python' → 'LearningRecommender python'
- 'how to learn machine learning' → 'LearningRecommender machine learning'
- 'study roadmap for bioinformatics' → 'LearningRecommender bioinformatics'
- 'best tutorials for scanpy' → 'LearningRecommender scanpy'
- 'what is the best course for data science?' → 'LearningRecommender data science'

-> Respond with 'general ( query )' if a query can be answered by a chatbot.
-> Respond with 'realtime ( query )' if a query requires up-to-date information.
-> Respond with 'open (app)', 'close (app)', 'play (song)', 'generate image (prompt)', etc.
-> Respond with 'iot <device> <action>' for IoT commands.

If unsure, respond with 'general (query)'.
"""

# Updated chat history with examples
ChatHistory = [
    {"role": "User", "message": "recommend resources for python"},
    {"role": "Chatbot", "message": "LearningRecommender python"},
    {"role": "User", "message": "how do I learn scanpy?"},
    {"role": "Chatbot", "message": "LearningRecommender scanpy"},
    {"role": "User", "message": "create a study roadmap for machine learning"},
    {"role": "Chatbot", "message": "LearningRecommender machine learning"},
]

def FirstLayerDMM(prompt: str = "test"):
    message.append({"role": "user", "content": f"{prompt}"})
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation="OFF",
        connectors=[],
        preamble=preamble
    )
    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text
    response = response.replace("\n", "").strip()
    response = response.split(",")
    response = [i.strip() for i in response]
    
    # Post-process standardized outputs
    temp = []
    for task in response:
        task_lower = task.lower()
        
        if task_lower.startswith("iot"):
            parts = task.split(" ")
            if len(parts) >= 3:
                device = parts[1]
                action = parts[2]
                if device.lower() in ["light", "lights"]:
                    device = "light"
                if action.lower() in ["on", "off"]:
                    task = f"iot {device} {action}"
            temp.append(task)

        elif any(task_lower.startswith(func.lower()) for func in funcs):
            temp.append(task)

    if not temp:
        temp = [f"general {prompt}"]

    # ✅ cleanup parentheses
    cleaned = []
    for t in temp:
        t = t.replace("(", "").replace(")", "").strip()
        cleaned.append(t)

    return cleaned

if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>>")))
