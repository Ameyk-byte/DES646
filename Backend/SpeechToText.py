from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not specified

# Define the HTML code for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language placeholder in the HTML code
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the HTML code to a file
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Configure Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Set up the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define temporary directory path
current_dir = os.getcwd()
TempDirPath = f"{current_dir}/Frontend/Files"

# Ensure the temporary directory exists
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Write the assistant's status to a file."""
    with open(f"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    """Modify the query to ensure proper punctuation and capitalization."""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    if any(word in new_query for word in question_words):
        if new_query[-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if new_query[-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def UniversalTranslate(Text):
    """Translate text to English."""
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    """Perform speech recognition and return the recognized text."""
    try:
        # Open the HTML file in the browser
        driver.get(f"file:///{os.path.abspath('Data/Voice.html')}")
        
        # Start speech recognition
        driver.find_element(By.ID, "start").click()
        
        # Wait for the output text
        while True:
            Text = driver.find_element(By.ID, "output").text.strip()
            if Text:
                driver.find_element(By.ID, "end").click()
                
                # Translate if necessary
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslate(Text))
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        return None

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print(Text)