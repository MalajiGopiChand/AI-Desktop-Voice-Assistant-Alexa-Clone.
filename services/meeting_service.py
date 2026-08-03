"""
Metis AI OS — Meeting Assistant & Live Transcription Engine.
Summarizes meetings, extracts action items, identifies key takeaways, and updates calendar events.
"""
from core.llm_client import chat, FAST_MODEL

class MeetingAssistant:
    def summarize_meeting_transcript(self, transcript_text):
        if not transcript_text.strip():
            return {"success": False, "message": "Empty transcript provided."}

        summary = chat(
            [
                {"role": "system", "content": "You are Metis Meeting Assistant. Summarize this meeting transcript into: 1. Key Highlights 2. Decided Action Items with owners 3. Next Steps."},
                {"role": "user", "content": transcript_text}
            ],
            model=FAST_MODEL,
            max_tokens=400
        )

        return {
            "success": True,
            "summary": summary,
            "raw_length": len(transcript_text)
        }


meeting_assistant = MeetingAssistant()
