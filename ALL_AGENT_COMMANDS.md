# 📜 METIS AI OS — ALL AGENT COMMANDS MASTER REFERENCE MANUAL

This document provides a comprehensive cheat-sheet of all voice and text commands executable across the **16 Specialized Agents** of the Metis AI Operating System.

---

## 1. 🖥️ DesktopAgent (`agents/desktop_agent.py`)
Controls Windows Desktop GUI, application launchers, window management, audio volume, and system power.

- `open notepad` — Opens Microsoft Notepad
- `open chrome` — Opens Google Chrome Browser
- `open chrome profile Work` — Opens Chrome with a specific user profile
- `open calculator` — Opens Windows Calculator
- `open vs code` — Opens Visual Studio Code
- `open task manager` — Opens Windows Task Manager
- `open cmd` — Opens Command Prompt
- `open paint` — Opens MS Paint
- `open word` — Opens Microsoft Word
- `open excel` — Opens Microsoft Excel
- `take screenshot` — Captures current screen and saves to screenshots directory
- `close window` — Closes currently active desktop window
- `mute volume` / `unmute volume` — Toggles system audio mute
- `volume up` / `volume down` — Adjusts system audio volume levels
- `lock computer` — Locks Windows desktop session
- `shutdown system` — Requests system shutdown (triggers safety confirmation)

---

## 2. 👁️ VisionAgent (`agents/vision_agent.py`)
Performs PyTesseract computer vision OCR, screen text analysis, and coordinate target mouse clicking.

- `read screen` / `read my screen` — Performs OCR text extraction on visible desktop screen
- `describe screen` — Captures screen and provides an AI vision summary of open windows
- `find and click [Text]` — Locates text coordinates on screen and clicks target element
- `click button [Name]` — Finds target UI button by text label and executes mouse click

---

## 3. 📱 MobileAgent (`agents/mobile_agent.py`)
Manages Android companion features, phone dialer calls, SMS drafting, alarm scheduler, and notifications.

- `call [Contact Name]` — Opens phone dialer and initiates call (e.g. *"call Master Gopi"*)
- `dial [Phone Number]` — Dials phone number directly (e.g. *"dial 9876543210"*)
- `send sms to [Contact] saying [Message]` — Drafts and sends SMS message
- `set alarm for [Time]` — Schedules device alarm (e.g. *"set alarm for 6:30 AM"*)
- `read notifications` — Fetches and summarizes recent mobile phone notifications
- `toggle flashlight on` / `toggle flashlight off` — Controls device torch/flashlight
- `rephrase chat [Text]` — Rephrases text message into professional, friendly, or formal tone

---

## 4. 💬 CommsAgent (`agents/comms_agent.py`)
Automates messaging protocols including WhatsApp Web, Gmail drafting, popup explainer, and command lists.

- `open whatsapp` — Opens WhatsApp Web in browser
- `send whatsapp message to [Contact]: [Message]` — Finds contact, types message, and sends
- `open chat with [Contact]` — Opens specific WhatsApp conversation window
- `type message [Text]` — Types message in active chat window
- `send message` — Presses Enter to dispatch chat message
- `compose email to [Address]` — Opens email composer with recipient
- `explain popup` — Analyzes current screen popup dialog and explains action options
- `show commands cheat sheet` — Renders command cheat-sheet view in Web UI

---

## 5. 🌐 BrowserAgent (`agents/browser_agent.py`)
Executes automated Playwright & Chromium web browsing, search queries, and webpage scraping.

- `search google for [Query]` — Performs Google search and opens top results
- `open website [URL]` — Navigates directly to specified web address (e.g. *"open github.com"*)
- `read page text` — Extracts clean text content from currently open webpage
- `fill form field [Name] with [Value]` — Types data into active web input field

---

## 6. 🔬 ResearchAgent (`agents/research_agent.py`)
Performs live web research using DuckDuckGo, Wikipedia article retrieval, and topic comparisons.

- `search duckduckgo for [Topic]` — Queries DuckDuckGo for live web search results
- `search wikipedia for [Topic]` — Retrieves summary paragraph from Wikipedia
- `summarize article [URL]` — Fetches article content and provides concise bullet summary
- `compare [Topic A] and [Topic B]` — Conducts comparative research analysis

---

## 7. 💻 CodingAgent (`agents/coding_agent.py`)
Assists in software development: code generation, snippet explanation, traceback debugging, and git status.

- `generate python script to [Task]` — Writes complete Python code script
- `generate javascript code for [Task]` — Writes modern JS ES6+ function
- `explain code [Snippet]` — Explains code structure, parameters, and logic
- `debug traceback [Error Log]` — Analyzes error stack trace and provides fix
- `check git status` — Runs local git status check on workspace repository

---

## 8. ⚡ AutomationAgent (`agents/automation_agent.py`)
Parses complex multi-step human instructions into macro automation JSON execution sequences.

- `automate: open chrome, wait 2 seconds, search for weather`
- `automate: open notepad, type Hello World, save file`
- `run macro [Macro Name]` — Triggers pre-recorded automation sequence

---

## 9. 🗣️ ConversationAgent (`agents/conversation_agent.py`)
Handles general conversational Q&A, natural language dialogue, and philosophical questions via Groq/Mistral LLM.

- `who was [Famous Person]` — Provides historical biography
- `explain [Concept] in simple terms` — Breaks down complex topics
- `give me advice on [Topic]` — Generates thoughtful recommendations
- `tell me a joke` / `tell me a story` — Generates creative conversational responses

---

## 10. 📅 CalendarAgent (`agents/calendar_agent.py`)
Integrates with Google Calendar API to manage events, reminders, and daily schedule agendas.

- `what's on my calendar today` — Fetches today's scheduled meetings and events
- `list upcoming events` — Shows next 7 days calendar entries
- `create reminder for [Event] at [Time]` — Adds new event to Google Calendar

---

## 11. 📄 OfficeAgent (`agents/office_agent.py`)
Processes Word documents (.docx), Excel spreadsheets (.xlsx), PDFs (.pdf), and PowerPoint (.pptx).

- `read file [Filename.pdf]` — Extracts text content from PDF document
- `summarize document [Filename.docx]` — Generates executive summary of Word doc
- `create word report about [Topic]` — Generates formatted Word (.docx) report document
- `read excel file [Filename.xlsx]` — Reads tabular data from Excel sheet

---

## 12. 📊 AnalyticsAgent (`agents/analytics_agent.py`)
Analyzes CSV/Excel datasets using Pandas, generates Matplotlib visualizations, and queries SQL databases.

- `analyze dataset [Filename.csv]` — Computes summary statistics (mean, median, nulls)
- `create bar chart for [Filename.csv]` — Plots Matplotlib bar chart and saves PNG image
- `create line chart for [Data]` — Generates time-series line plot
- `query database [SQL Query]` — Executes SQLite/MySQL data query safely

---

## 13. 🧮 MathAgent (`agents/math_agent.py`)
Solves arithmetic, algebra, calculus (derivatives & integrals via SymPy), and plots mathematical functions.

- `calculate [Expression]` — Evaluates math expression (e.g. *"calculate 73 * 15 + 42"*)
- `solve equation [Equation]` — Solves algebraic equation (e.g. *"solve equation x**2 - 9 = 0"*)
- `differentiate [Function]` — Computes calculus derivative (e.g. *"differentiate x**3 + 2*x"*)
- `integrate [Function]` — Computes calculus integral
- `plot function [Function]` — Generates 2D function graph

---

## 14. 📁 FileAgent (`agents/file_agent.py`)
Manages filesystem search, Downloads folder cleanup, file organization, and duplicate file hash detection.

- `search files for [Pattern]` — Searches workspace directory for matching files
- `organize Downloads folder` — Categorizes files into Images, Documents, Videos, Archives
- `find duplicate files` — Scans directory using MD5 hashes to detect exact duplicate files
- `get file info [Filename]` — Shows file size, modification date, and permissions

---

## 15. 🎵 MediaAgent (`agents/media_agent.py`)
Controls HTML5 media player playback in browsers, YouTube video playback, and Spotify launcher.

- `play video` / `pause video` — Controls video playback on active browser tab
- `seek forward 10 seconds` / `seek back 10 seconds` — Rewinds or fast-forwards media
- `full screen` / `exit full screen` — Toggles media video player fullscreen
- `mute video` / `unmute video` — Toggles audio track mute state
- `play lofi music on youtube` — Opens YouTube and starts music playback
- `open spotify` — Launches Spotify application

---

## 16. 🌤️ InfoAgent (`agents/info_agent.py`)
Retrieves live weather data via OpenWeatherMap API and tech news via RSS feeds & NewsAPI.

- `what is the weather in [City]` — Returns live temperature, humidity, and forecast (e.g. *"weather in Mumbai"*)
- `latest tech news` — Fetches top headlines from BBC Tech and Hacker News RSS feeds
- `system status` — Returns CPU %, RAM %, battery status, and active agent count

