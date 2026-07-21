# AI Desktop Voice Assistant

An intelligent desktop assistant that listens to voice commands, converts speech to text, processes commands, executes desktop tasks, and responds using a natural voice. Built entirely in Python.

## Features
- **Speech Recognition:** Listens to your voice and converts it to text.
- **Text-to-Speech:** Speaks back to you naturally using `pyttsx3`.
- **Desktop Automation:** Automates tasks like opening apps, taking screenshots, and controlling volume.
- **System Information:** Reports CPU, RAM, and Battery status.
- **Web Search:** Searches Wikipedia, Google, and YouTube, or opens specific websites.
- **Database Logging:** Saves all commands and their execution status locally using SQLite3.

## Folder Structure
```text
AI-Desktop-Assistant/
├── main.py              # Entry point
├── assistant.py         # Core engine loop
├── speech.py            # Audio input/output
├── commands.py          # Command router
├── database.py          # SQLite database management
├── config.py            # Global settings
├── utils.py             # Action executors
├── database/            # Contains assistant.db
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Installation & Requirements

1. Make sure you have Python 3.13+ installed.
2. Open a terminal in this directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
*(Note: If you run into issues with PyAudio, you may need to install the PyAudio wheel manually or install build tools for your OS.)*

## Usage

1. Run the assistant:
   ```bash
   python main.py
   ```
2. The assistant will greet you. Say the wake word `"Jarvis"` or `"Hello Assistant"` to activate listening.
3. After the assistant says "Yes?", give a command like:
   - "Open Notepad"
   - "What time is it?"
   - "System Info"
   - "Search Wikipedia for Python"
   - "Take a screenshot"
4. Say "Exit" or press `Ctrl+C` in the terminal to stop the assistant.

## Common Bugs & Solutions
- **PyAudio Installation Error:** If `pip install pyaudio` fails on Windows, download the corresponding PyAudio `.whl` file for your Python version and install it directly via pip.
- **Microphone Not Detected:** Ensure your default microphone is set properly in Windows Sound Settings and privacy settings allow desktop apps to access the microphone.
- **No Internet Error:** `speech_recognition` requires an internet connection for the Google API. Check your connection.

## Future Improvements
- Face Recognition Login
- ChatGPT / Gemini API Integration
- Weather & News APIs
- WhatsApp Automation
- Spotify Control
- Smart Scheduling

## License
MIT License
