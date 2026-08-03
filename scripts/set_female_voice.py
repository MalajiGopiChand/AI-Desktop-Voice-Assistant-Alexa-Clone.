try:
    import pythoncom
    pythoncom.CoInitialize()
except Exception:
    pass

import pyttsx3
from database import set_setting

engine = pyttsx3.init()
voices = engine.getProperty("voices")
zira_voice = next((v for v in voices if "zira" in v.name.lower() or "female" in v.name.lower()), None)

if zira_voice:
    set_setting("voice_id", zira_voice.id)
    set_setting("voice", zira_voice.id)
    print(f"Female voice set to: {zira_voice.name} ({zira_voice.id})")
elif len(voices) > 1:
    set_setting("voice_id", voices[1].id)
    set_setting("voice", voices[1].id)
    print(f"Female voice set to: {voices[1].name} ({voices[1].id})")
else:
    print("Default voice set.")
