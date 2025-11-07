from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

# Ensure the Data directory exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Define the RealtimeInformation function
def RealtimeInformation():
    """Generate real-time information."""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# Initialize chat messages
messages = []
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "system", "content": RealtimeInformation()}  # Call RealtimeInformation here
]

# Load or initialize chat log
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
        # Validate roles in loaded messages
        for msg in messages:
            if msg["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid role found in chat log: {msg['role']}")
except FileNotFoundError:
    with open(r"Data/ChatLog.json", "w") as f:
        dump([], f)
except ValueError as e:
    print(f"Error in chat log: {e}")
    messages = []  # Reset messages if invalid data is found

def AnswerModification(Answer):
    """Remove empty lines from the answer."""
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def ChatBot(Query):
    """Send user query to the chatbot and return the AI's response."""
    global messages  # Use global variable to persist chat history
    try:
        # Append user message
        messages.append({"role": "user", "content": Query})

        # Generate completion
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None,
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                Answer = Answer.replace("</s>", "")

        # Append assistant message
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open(r"Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModification(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Reset chat log on error
        with open(r"Data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))