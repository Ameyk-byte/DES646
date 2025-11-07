# Nuero Personal Assistant (Personalized Learning Recommender)

## Overview
This project is a **Personal Assistant** developed by group **Synapse** using **Python 3.10**. The assistant is designed to Personalize Learning. It also integrates multiple models and automation scripts to provide accurate responses, real-time data retrieval, task automation, image generation, and IoT control.

## Installation
### Prerequisites
Ensure you have Python 3.10 installed on your system. Then, install the required dependencies using:
```bash
pip install -r Requirements.txt
```

## Project Structure
The project consists of multiple Python scripts, each handling different functionalities.

### 1. **Model Classification (model.py)**
- This script classifies user queries into predefined categories:
  - **Exit**
  - **General**
  - **Realtime**
  - **Open**
  - **Close**
  - **Play**
  - **Generate Image**
  - **System**
  - **Content**
  - **Google Search**
  - **YouTube Search**
  - **Reminder**
  - **IoT**
- If the query is general, it is processed using `Chatbot.py`.
- If the query is real-time, it is handled by `RealtimeSearchEngine.py`.
- Other query types are managed using `Automation.py`.

### 2. **General Query Processing (Chatbot.py)**
- Uses **Gradio (Gravq) UI** and **LLaMA 70B** model to process user queries.
- Includes specific instructions to behave like a personal assistant.

### 3. **Real-Time Data Search (RealtimeSearchEngine.py)**
- Uses **Google Search API** to fetch real-time and accurate data for user queries.

### 4. **Automation Tasks (Automation.py)**
- Handles various automation tasks such as:
  - Opening applications/websites
  - Closing applications
  - Playing media files
  - System controls (volume, brightness, etc.)

### 5. **Image Generation (ImageGeneration.py)**
- Generates images based on user inputs.
- Uses AI-based image generation models.

### 6. **IoT Control (IoT.py)**
- Handles IoT-related instructions.
- Uses `iot.data` to store and manage IoT devices.

## Usage
Run the assistant using the following command:
```bash
python main.py
```

## Features
- **Intelligent Query Classification**: Classifies user queries for efficient processing.
- **LLaMA 70B Chatbot**: Provides conversational responses.
- **Real-Time Search**: Fetches accurate real-time data using Google Search.
- **Task Automation**: Opens, closes applications, and controls system settings.
- **AI Image Generation**: Generates images based on text input.
- **IoT Device Management**: Controls IoT devices.




