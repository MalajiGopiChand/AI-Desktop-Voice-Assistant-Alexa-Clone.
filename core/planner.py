import json
from core.llm_client import chat, DEFAULT_MODEL
from core.memory import memory


AGENT_CATALOG = """
desktop_agent: open_app, type, press, hotkey, wait, screenshot, switch_window, close_window,
  open_folder, move_file, rename_file, delete_file (confirm), shutdown/restart/lock/sleep (confirm)

browser_agent: open_url, search, read_page, open_with_profile,
  automate_search (Playwright: search + open first result), automate_navigate, automate_read, automate_fill_form

research_agent: search_web, search_wikipedia, summarize, ask_llm, compare

vision_agent: screenshot, read_screen, ocr_region, describe_screen

comms_agent: open_email, compose_email, send_email (confirm), open_whatsapp, send_whatsapp (confirm)

coding_agent: generate_code, explain_code, fix_code, run_code, git_status

automation_agent: parse_and_run, run_workflow

calendar_agent: list_events, create_reminder, today_schedule

office_agent: read_word, write_word, read_excel, summarize_excel, read_pdf, summarize_pdf, create_report, read_pptx

analytics_agent: analyze_csv, create_chart, sql_query, describe_data, predict_trend

math_agent: calculate, solve_equation, differentiate, integrate, plot_function, statistics

file_agent: search_files, find_duplicates, organize_folder, index_folder

media_agent: play_pause, next_track, previous_track, volume_up, volume_down, open_spotify

info_agent: weather, news, headlines

memory_agent: save_fact, set_preference

voice_agent: speak(text) — always end plan with summary

conversation_agent: chat(message)
"""


class PlannerEngine:
    def generate_plan(self, user_command):
        context_msgs = memory.get_context(limit=6)
        context_str = "\n".join(f"{m['role']}: {m['content']}" for m in context_msgs)
        facts = memory.recall_facts(limit=5)
        fact_str = "\n".join(f"- {f}" for f in facts) if facts else "None"

        system_prompt = f"""You are the JARVIS AI Planner. Break commands into a sequential JSON execution plan.

{AGENT_CATALOG}

Rules:
- Output ONLY a raw JSON array. No markdown.
- Always end with voice_agent speak summarizing results.
- Use browser_agent automate_* for full browser workflows (search, read, fill forms).
- Use info_agent for weather/news. Use calendar_agent for schedule/reminders.
- Use office_agent for documents. Use analytics_agent for CSV/charts.
- Use math_agent for calculations. Use file_agent for file search/organize.
- Use memory_agent when user shares personal info.

Example:
[
  {{"agent":"browser_agent","action":"automate_search","params":{{"query":"OpenAI official website"}}}},
  {{"agent":"browser_agent","action":"automate_read","params":{{}}}},
  {{"agent":"research_agent","action":"summarize","params":{{"text":"{{{{prev}}}}"}}}},
  {{"agent":"voice_agent","action":"speak","params":{{"text":"Here is the summary."}}}}
]"""

        prompt = f"Context:\n{context_str}\n\nFacts:\n{fact_str}\n\nCommand: {user_command}"

        try:
            raw = chat(
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                model=DEFAULT_MODEL,
                max_tokens=1000,
                temperature=0.1,
            )
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            plan = json.loads(raw.strip())
            return {"plan": plan}
        except json.JSONDecodeError:
            return {"error": "Failed to parse planner JSON output."}
        except Exception as e:
            return {"error": str(e)}


planner = PlannerEngine()
