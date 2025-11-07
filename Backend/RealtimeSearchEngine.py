from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

# Ensure the Data directory exists
import os
if not os.path.exists("Data"):
    os.makedirs("Data")

# Initialize chat messages
messages = []
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way and do not use points use paragraph. ***"""

SystemChatBot = [{"role": "system", "content": System}]

try:
    with open("Data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    """Perform a Google search and return formatted results."""
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\nURL: {i.url}\n\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"An error occurred while searching: {e}"

def AnswerModifier(Answer):
    """Remove empty lines from the answer."""
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def Information():
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

def RealtimeSearchEngine(prompt):
    """Handle user queries with real-time search and AI response."""
    global messages
    try:
        # Load chat log
        with open("Data/ChatLog.json", "r") as f:
            messages = load(f)

        # Append user message
        messages.append({"role": "user", "content": prompt})

        # Perform Google search
        search_results = GoogleSearch(prompt)

        # Generate completion
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + [{"role": "system", "content": search_results}] + messages,
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
        with open("Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Reset chat log on error
        with open("Data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Please try again."

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))