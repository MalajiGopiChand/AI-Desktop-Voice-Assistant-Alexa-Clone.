"""
Configuration Settings for the AI Desktop Voice Assistant.
This file serves as the single source of truth for constants.
Any changes to the assistant's behavior, like its name or voice speed,
should be made here.
"""

# The word the assistant listens for before executing a command
WAKE_WORD = "jarvis"
ALT_WAKE_WORD = "hello assistant"

# Voice Settings
VOICE_RATE = 175        # Speed of speech (words per minute). Higher is faster.
VOICE_VOLUME = 1.0      # Volume level (0.0 to 1.0)
VOICE_INDEX = 1         # 0 for male, 1 for female (depends on the operating system's installed voices)

# User Information
USERNAME = "Gopi"
ASSISTANT_NAME = "Jarvis"

# Paths
DATABASE_PATH = "database/assistant.db"

# Timeout for speech recognition
LISTEN_TIMEOUT = 5      # Seconds to wait for a phrase to start
PHRASE_TIME_LIMIT = 10  # Maximum seconds a phrase can last
