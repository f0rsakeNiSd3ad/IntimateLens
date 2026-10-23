# IntimacyLens - Relationship Health Analysis

A local-first, privacy-focused application that analyzes relationship dynamics and communication health using on-device psychological frameworks (Gottman Method, Attachment Theory) and deterministic NLP telemetry.

---

## Quick Start (For Simple Use, Use the .bat Files!)

> **Why overcomplicate things for no reason?**  
> IntimacyLens comes with 1-click batch files right in the root folder so you don't have to deal with multiple terminals, manual commands, or activating virtual environments.

### 1. First-Time Setup (Run Once)
Double-click **`setup.bat`**
* Automatically checks Python 3.10+ and Node.js 18+.
* Configures the Python backend environment and installs dependencies.
* Installs frontend packages and builds the optimized web app.

### 2. Launching IntimacyLens (Everyday Use)
Double-click **`start.bat`**
* Automatically launches the FastAPI backend (`http://127.0.0.1:8001`).
* Automatically launches the Next.js frontend (`http://localhost:3000`).
* Runs real-time health checks and **opens your browser automatically** the moment services are ready.
* Keeps a single, clean controller dashboard.

### 3. Clean Shutdown
* Simply **press any key** inside the `start.bat` controller window, or double-click **`stop.bat`** to terminate all background servers cleanly.

---

## Overview & Key Capabilities

IntimacyLens allows you to upload raw text or JSON exports of your conversations (WhatsApp, Instagram, SMS) and analyzes communication health using validated psychological frameworks:

* **Gottman Four Horsemen Telemetry:** Accurately detects and scores **Criticism**, **Contempt**, **Defensiveness**, and **Stonewalling**.
* **Context-Aware Conflict De-escalation:** Evaluates genuine Gottman Repair Attempts only within active tension windows, avoiding false positives.
* **Work-Hour Autonomy Protection:** Daytime response pauses (9:00 AM – 5:00 PM) are never penalized as apathy or emotional disconnection.
* **Sarcasm & Insult Disambiguation:** Demeaning phrases ("Oh, poor baby... God, you're so useless") are identified as Contempt with heavy penalties, never misclassified as affection.
* **Dual Blueprint Output:**
  - **Healthy & Thriving Chats:** Routes to the *Relationship Vitality & Connection Blueprint* with proactive Gottman Sound Relationship House connection rituals.
  - **Friction & Crisis Chats:** Routes to the *Relationship Repair Blueprint* with "The Brutal Truth" and structured de-escalation protocols.
* **100% Local & Privacy-First:** All processing is done locally on your machine. Zero chat data leaves your device.

---

## Supported Chat Export Formats

* **WhatsApp (Bracket format):**  
  `[12/10/2023, 14:30:00] Alice: Hey, how are you?`
* **WhatsApp (Dash & Unicode LTR format):**  
  `12/10/2023, 2:30 PM - Bob: Stuck in a meeting, talk soon!`
* **Instagram Direct Message Exports:**  
  `Alice (12/10/2023, 18:00): Did you see this?`
* **Plain Text SMS & Transcripts:**  
  `Alice: Hello there!`
* **JSON Chat Exports:**  
  Array of objects containing `sender`/`author` and `text`/`message` keys.

---

## Advanced / Manual Developer Setup (CLI / Linux / macOS)

If you are not on Windows or prefer running services manually via command line:

### Prerequisites
* Python 3.10+
* Node.js 18+ & npm

### 1. Clone the Repository
```bash
git clone https://github.com/f0rsakeNiSd3ad/IntimateLens.git
cd IntimateLens
```

### 2. Manual Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic python-multipart httpx

# Start the backend server on port 8001
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Manual Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

### 4. Open in Browser
Open `http://localhost:3000` in your web browser.

---

## Running Verification Tests

To verify the deterministic psychological engine against all 14 clinical test scenarios (covering WhatsApp formats, Gottman metrics, work-hour autonomy, mutual exclusivity, and sarcasm detection):

```bash
python backend/test_suite.py
```

---

## Privacy & Security

* **Local Processing:** IntimacyLens runs completely on-device. No telemetry, chat logs, or personal metrics are transmitted to any cloud servers.
* **No API Keys Required:** Operates deterministically without third-party LLM cloud subscriptions.
* **Disclaimer:** IntimacyLens is an analytical self-reflection tool. It is not licensed psychological or psychiatric counsel.

---

## License

This project is licensed under the MIT License.
